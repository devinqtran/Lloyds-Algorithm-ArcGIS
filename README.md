# Lloyd’s Algorithm Optimization Tool for ArcGIS Pro

![ArcGIS Pro](https://img.shields.io/badge/ArcGIS%20Pro-3.x-green)
![Python](https://img.shields.io/badge/Python-3.x-yellow)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

<p align="center">
  <img src="docs/images/lloyds_icon_voronoi.png" width="400" title="Lloyd's Algorithm Optimization">
</p>

## 📌 Project Overview

This tool is designed for urban planners and GIS researchers to optimize facility placement based on the distribution of demand points. Unlike static placement, this engine iteratively moves facility locations to the geographic center (centroid) of their assigned service areas until an optimal state is reached.

## 🚀 Key Features

- **Iterative Optimization:** Automatically re-calculates weighted centroids and re-assigns points until spatial convergence is achieved.
- **Performance Metrics:** Reports an **Objective Function (Total Euclidean Distance)** and calculates the total efficiency improvement percentage in the Geoprocessing messages.
- **Comprehensive Visual Outputs:** Generates final facilities, point assignment layers, Voronoi (Thiessen) service areas, and a full visual history of the facility migration.
- **Custom Initialization:** Supports a **Random Seed** parameter to ensure reproducibility during testing and analysis.

## 🛠 Technical Implementation

The core engine is built in Python using **ArcPy**, utilizing a modular class structure for both the algorithm logic and the output management.

- **Logic:** The tool implements Centroidal Voronoi Tessellation logic to find optimal point distributions.
- **Termination:** The loop breaks automatically when the maximum facility movement falls below the user-defined **Convergence Threshold**.
- **Symbology:** Uses an automated symbology function to apply consistent colors and transparency to output layers immediately upon addition to the map.

## 📖 Tool Parameters

| Parameter                 | Type          | Description                                          |
| :------------------------ | :------------ | :--------------------------------------------------- |
| **Input Demand Points**   | Feature Layer | The points representing demand or population.        |
| **Facility Count**        | Long          | The number of facilities to optimize.                |
| **Max Iterations**        | Long          | Safety cutoff for the optimization loop.             |
| **Convergence Threshold** | Double        | The movement distance at which the tool stops.       |
| **Random Seed**           | Long          | Controls the initial random placement of facilities. |

## 📂 Repository Structure

- `scripts/`: Contains `lloyds_engine.py`, the core Python logic.
- `toolbox/`: Contains `LloydsOptimization.atbx`, the ArcGIS Pro tool interface.
- `data/`: Includes sample datasets for testing the optimization engine.
- `docs/`: Documentation, tool icons, and demo GIFs.

---

## 🎓 About the Author

Developed as part of a GIS portfolio by a **Geography Student at Brigham Young University**. This project demonstrates the integration of spatial theory, Python automation, and professional GIS tool development.
