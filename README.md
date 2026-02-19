# Lloyd’s Algorithm Optimization Tool for ArcGIS Pro

![ArcGIS Pro](https://img.shields.io/badge/ArcGIS%20Pro-3.x-green)
![Python](https://img.shields.io/badge/Python-3.x-yellow)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

An automated spatial optimization tool that implements **Lloyd’s Algorithm** (Centroidal Voronoi Tessellation) to solve location-allocation problems within the ArcGIS Pro environment.

---

## 📌 Project Overview

[cite_start]This tool is designed for urban planners and GIS researchers to optimize facility placement based on the distribution of demand points[cite: 1, 3]. [cite_start]Unlike static placement, this engine iteratively moves facility locations to the geographic center (centroid) of their assigned service areas until an optimal state is reached[cite: 1, 3].

## 🚀 Key Features

- [cite_start]**Iterative Optimization:** Automatically re-calculates weighted centroids and re-assigns points until spatial convergence is achieved[cite: 1, 3].
- [cite_start]**Performance Metrics:** Reports an **Objective Function (Total Euclidean Distance)** and calculates the total efficiency improvement percentage in the Geoprocessing messages[cite: 1, 3].
- [cite_start]**Comprehensive Visual Outputs:** Generates final facilities, point assignment layers, Voronoi (Thiessen) service areas, and a full visual history of the facility migration[cite: 1, 3].
- [cite_start]**Custom Initialization:** Supports a **Random Seed** parameter to ensure reproducibility during testing and analysis[cite: 1, 3].

## 🛠 Technical Implementation

[cite_start]The core engine is built in Python using **ArcPy**, utilizing a modular class structure for both the algorithm logic and the output management[cite: 3].

- **Logic:** $P_{i+1} = \frac{1}{M_i} \iint_{V_i} x \cdot \rho(x) dA$
- [cite_start]**Termination:** The loop breaks automatically when the maximum facility movement falls below the user-defined **Convergence Threshold**[cite: 1, 3].
- [cite_start]**Symbology:** Uses an automated symbology function to apply consistent colors and transparency to output layers immediately upon addition to the map[cite: 3].

## 📖 Tool Parameters

| Parameter                 | Type          | Description                                                                  |
| :------------------------ | :------------ | :--------------------------------------------------------------------------- |
| **Input Demand Points**   | Feature Layer | [cite_start]The points representing demand or population[cite: 1, 3].        |
| **Facility Count**        | Long          | [cite_start]The number of facilities to optimize[cite: 1, 3].                |
| **Max Iterations**        | Long          | [cite_start]Safety cutoff for the optimization loop[cite: 1, 3].             |
| **Convergence Threshold** | Double        | [cite_start]The movement distance at which the tool stops[cite: 1, 3].       |
| **Random Seed**           | Long          | [cite_start]Controls the initial random placement of facilities[cite: 1, 3]. |

## 📂 Repository Structure

- [cite_start]`scripts/`: Contains `lloyds_engine.py`, the core Python logic[cite: 1, 3].
- [cite_start]`toolbox/`: Contains `LloydsOptimization.atbx`, the ArcGIS Pro tool interface[cite: 1].
- `data/`: Includes sample datasets for testing the optimization engine.
- `docs/`: Documentation, tool icons, and demo GIFs.

---

## 🎓 About the Author

Developed as part of a GIS portfolio by a **Geography Student at Brigham Young University**. This project demonstrates the integration of spatial theory, Python automation, and professional GIS tool development.
