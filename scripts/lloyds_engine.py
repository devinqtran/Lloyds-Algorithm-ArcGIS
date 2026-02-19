import arcpy
import math
import random
import os

# Euclidean distance method (faster than ESRI tool)
class GeometryUtils:
    @staticmethod
    def euclidean_distance(x1, y1, x2, y2):
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

# Initialize LloydsAlgorithm class 
class LloydsAlgorithm:
    def __init__(self, num_facilities, max_iterations, convergence_threshold, random_seed=42):
        self.num_facilities = num_facilities
        self.max_iterations = max_iterations
        self.convergence_threshold = convergence_threshold
        self.random_seed = random_seed
        self.geo_utils = GeometryUtils()

    # Main algorithm execution
    def run(self, points):
        # Initialize random seed
        random.seed(self.random_seed)

        # Randomly select which input points become initial facility locations
        selected_indices = random.sample(range(len(points)), self.num_facilities)

        # Creates initial list of facility dictionaries, accesses and extracts xy values from idx (position in points list)
        facilities = [{"id": i, "x": points[idx]["xy"][0], "y": points[idx]["xy"][1]} 
                      for i, idx in enumerate(selected_indices)]
        
        # Track each iteration store in iteration_history
        iteration_history = []
        arcpy.AddMessage(f"{'Iteration':<12} | {'Objective Function (Total Distance)':<35}")
        arcpy.AddMessage("-" * 50)

        # Loop for iterations
        for iteration in range(self.max_iterations):
            # Assignment Step
            assignments = []
            # Nested loop for each point
            for p in points:
                dists = [self.geo_utils.euclidean_distance(p["xy"][0], p["xy"][1], f["x"], f["y"]) for f in facilities]
                assignments.append(dists.index(min(dists)))
            
            # Metrics Calculation
            total_dist = sum(self.geo_utils.euclidean_distance(points[i]["xy"][0], points[i]["xy"][1], 
                             facilities[assignments[i]]["x"], facilities[assignments[i]]["y"]) for i in range(len(points)))
            
            # Print Objective Function for current iteration
            arcpy.AddMessage(f"{iteration + 1:<12} | {total_dist:<35,.2f}")
            
            # Track number of points assigned to each facility
            sizes = [assignments.count(i) for i in range(self.num_facilities)]
            iteration_history.append({
                "iteration": iteration + 1, "facilities": [f.copy() for f in facilities],
                "objective": total_dist, "assignments": assignments, "cluster_sizes": sizes
            })

            # Update Step (Centroids)
            new_facilities = []
            max_move = 0
            
            # Loop over each facility, move each facility to the centroid
            for f in facilities:
                pts = [points[i] for i, a in enumerate(assignments) if a == f["id"]]
                if not pts:
                    new_f = f.copy()
                else:
                    nx, ny = sum(p["xy"][0] for p in pts)/len(pts), sum(p["xy"][1] for p in pts)/len(pts)
                    new_f = {"id": f["id"], "x": nx, "y": ny}
                
                move = self.geo_utils.euclidean_distance(f["x"], f["y"], new_f["x"], new_f["y"])
                max_move = max(max_move, move)
                new_facilities.append(new_f)

            # Update facilities
            facilities = new_facilities
            # Track convergence threshold
            if max_move < self.convergence_threshold:
                arcpy.AddMessage(f"\nConverged! Max movement ({max_move:.4f}) is below threshold.")
                break
        # Returns complete iteration history with objective function values and point assignments
        return iteration_history
    
# Initialize class to manage ouputs and workspace
class OutputManager:
    def __init__(self, workspace, spatial_ref):
        self.workspace = workspace
        self.spatial_ref = spatial_ref
        self.geo_utils = GeometryUtils()

    # Method to create each output layer
    def create_outputs(self, history, points, f_name, i_name, a_name, v_name=None):
        # 1. Final Facilities
        out_f = arcpy.CreateFeatureclass_management(self.workspace, f_name, "POINT", spatial_reference=self.spatial_ref)
        arcpy.AddField_management(out_f, "Facility_ID", "LONG")
        with arcpy.da.InsertCursor(out_f, ["SHAPE@XY", "Facility_ID"]) as cur:
            for f in history[-1]["facilities"]: cur.insertRow([(f["x"], f["y"]), f["id"]])

        # 2. Iteration History
        out_i = arcpy.CreateFeatureclass_management(self.workspace, i_name, "POINT", spatial_reference=self.spatial_ref)
        arcpy.AddField_management(out_i, "Iteration", "LONG")
        arcpy.AddField_management(out_i, "Facility_ID", "LONG")
        with arcpy.da.InsertCursor(out_i, ["SHAPE@XY", "Iteration", "Facility_ID"]) as cur:
            for entry in history:
                for f in entry["facilities"]:
                    cur.insertRow([(f["x"], f["y"]), entry["iteration"], f["id"]])

        # 3. Assignments
        out_a = arcpy.CreateFeatureclass_management(self.workspace, a_name, "POINT", spatial_reference=self.spatial_ref)
        arcpy.AddField_management(out_a, "Assigned_Facility", "LONG")
        with arcpy.da.InsertCursor(out_a, ["SHAPE@XY", "Assigned_Facility"]) as cur:
            for i, p in enumerate(points): cur.insertRow([p["xy"], history[-1]["assignments"][i]])

        # 4. Voronoi
        if v_name:
            temp_pts = os.path.join("memory", "temp_fac")
            arcpy.CreateFeatureclass_management("memory", "temp_fac", "POINT", spatial_reference=self.spatial_ref)
            arcpy.AddField_management(temp_pts, "Facility_ID", "LONG")
            with arcpy.da.InsertCursor(temp_pts, ["SHAPE@XY", "Facility_ID"]) as cur:
                for f in history[-1]["facilities"]: cur.insertRow([(f["x"], f["y"]), f["id"]])
            
            arcpy.env.extent = arcpy.Describe(out_a).extent
            arcpy.analysis.CreateThiessenPolygons(temp_pts, os.path.join(self.workspace, v_name), "ALL")
            arcpy.Delete_management("memory")

# Method for adding custom symbology
def apply_symbology(lyr, sym_type):
    sym = lyr.symbology
    if sym_type in ['assignments', 'voronoi', 'iterations']:
        sym.updateRenderer('UniqueValueRenderer')
        if sym_type == 'assignments': field = "Assigned_Facility"
        elif sym_type == 'iterations': field = "Iteration"
        else: field = "Facility_ID"
        sym.renderer.fields = [field]
        if sym_type == 'voronoi': lyr.transparency = 50
    elif sym_type == 'facilities':
        sym.renderer.symbol.color = {'RGB': [230, 76, 60, 100]}
        sym.renderer.symbol.size = 14
    lyr.symbology = sym

# Main orchestration function to set up environment, load inputs, run algorithm, calculate stats, create output feature classes, and add styles/layers to map
def run_analysis(input_points, num_facilities, max_iterations, convergence_threshold, output_workspace, output_facilities, output_iterations, output_assignments, output_voronoi, random_seed):
    # Set up the environment
    arcpy.env.workspace = output_workspace
    arcpy.env.overwriteOutput = True
    
    # Retrieve spatial reference
    sr = arcpy.Describe(input_points).spatialReference

    # Read each point from input feature class using a SearchCursor, convert to a list of dictionaries [xy, oid]
    points = [{"xy": r[0], "oid": r[1]} for r in arcpy.da.SearchCursor(input_points, ["SHAPE@XY", "OID@"])]
    
    # Initialize algorithm, create new instance of LloydsAlgorithm using user parameters
    engine = LloydsAlgorithm(
        num_facilities=int(num_facilities), 
        max_iterations=int(max_iterations), 
        convergence_threshold=float(convergence_threshold), 
        random_seed=int(random_seed)
    )
    
    # Execute algorithm on the points, returns a list of dictionaries
    history = engine.run(points)
    
    # Performance metrics
    initial_obj = history[0]['objective']
    final_obj = history[-1]['objective']
    improvement = ((initial_obj - final_obj) / initial_obj) * 100 if initial_obj > 0 else 0
    
    # Print summary statistics
    arcpy.AddMessage("-" * 50)
    arcpy.AddMessage(f"SUMMARY STATISTICS")
    arcpy.AddMessage(f"Initial Distance: {initial_obj:,.2f}")
    arcpy.AddMessage(f"Final Distance:   {final_obj:,.2f}")
    arcpy.AddMessage(f"Total Improvement: {improvement:.2f}%")
    arcpy.AddMessage("-" * 50)

    # Create output files
    writer = OutputManager(output_workspace, sr)
    writer.create_outputs(history, points, output_facilities, output_iterations, output_assignments, output_voronoi)
    
    # Find current active map and add each layer
    m = arcpy.mp.ArcGISProject("CURRENT").activeMap
    if m:
        # Create list of tuples with feature class name and symbology type
        layers_to_add = [
            (output_voronoi, 'voronoi'), 
            (output_assignments, 'assignments'), 
            (output_iterations, 'iterations'), 
            (output_facilities, 'facilities')
        ]
        # Loop through each pair
        for name, s_type in layers_to_add:
            if name:
                try:
                    lyr_path = os.path.join(output_workspace, name)
                    if arcpy.Exists(lyr_path):
                        lyr = m.addDataFromPath(lyr_path)
                        apply_symbology(lyr, s_type)
                except: pass

# Entry point retrieves parameters from dialog
if __name__ == "__main__":
    run_analysis(
        input_points          = arcpy.GetParameterAsText(0),
        num_facilities        = arcpy.GetParameter(1),
        max_iterations        = arcpy.GetParameter(2),
        convergence_threshold = arcpy.GetParameter(3),
        output_workspace      = arcpy.GetParameterAsText(4),
        output_facilities     = arcpy.GetParameterAsText(5),
        output_iterations     = arcpy.GetParameterAsText(6),
        output_assignments    = arcpy.GetParameterAsText(7),
        output_voronoi        = arcpy.GetParameterAsText(8) if arcpy.GetParameterAsText(8) else None,
        random_seed           = arcpy.GetParameter(9) if arcpy.GetParameter(9) is not None else 42
    )