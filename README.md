# Stellar Mapping Project

This project is a Python-based pipeline for turning real astronomical catalog data into a 3D star map that can be visualized inside game engines. In this case Minecraft Java Edition 1.20.1 was used as the visualization tool. The project uses stellar catalog data from sources such as Gaia and Hipparcos, processes nearby stars, converts their coordinates into a 3D spatial system, and generates `.mcfunction` files that place the stars into the game environment.

The goal of this project was to make nearby star systems easier to understand visually. Instead of viewing stars only as numbers in a catalog, this project converts them into a spatial model so that distances, clusters, and relative positions can be explored directly.

## Project Overview

The pipeline performs several main steps:

1. Fetch or import astronomical star catalog data.
2. Clean and organize the dataset.
3. Match catalog entries with star names where available.
4. Filter stars within a selected distance range.
5. Convert astronomical coordinate data into 3D coordinates.
6. Scale the coordinates for visualization.
7. Generate Minecraft `.mcfunction` command files.
8. Package the generated files into a usable Minecraft datapack.

## Skills Demonstrated

This project demonstrates:

* Python programming
* Data cleaning and preprocessing
* Large dataset handling
* Coordinate transformations
* Scientific visualization
* Automated command generation
* File organization and data pipeline design
* 3D spatial reasoning

## Repository Structure

```text
stellar-mapping-project/
  src/
    Python scripts used for dataset processing, coordinate conversion, and command generation.

  data_sample/
    Small sample datasets used to demonstrate the workflow.

  outputs/
    Example generated coordinate files and command outputs.

  datapack/
    Ready-to-use Minecraft datapack files.

  screenshots/
    Images of the generated star map.

  docs/
    Additional explanation of the pipeline and project structure.
```

## Datapack Installation 

A ready-to-use datapack is included for anyone who wants to view the generated star map in Minecraft Java Edition.

### How to Install the Datapack

1. Download file 'starmap'
2. Go to %appdata% .minecraft folder or access the location of the world's save folder
3. Copy the 'starmap' folder into your Minecraft world’s `datapacks` folder. 

The path should look like this:

```text
.minecraft/saves/[Your World Name]/datapacks/[Datapack Folder]
```

4. Open the Minecraft world.
5. Run:

```mcfunction
/reload
```

6. Then run:

```mcfunction
/function starmap:install
```

This will start generating the star map.

## Important Note About Generation

The full star map is too large to generate reliably from one single `.mcfunction` file. Because of this, the placement commands are split into multiple smaller function files. The included `install.mcfunction` file schedules these placement functions over time, so the user only needs to run one command:

```mcfunction
/function starmap:install
```

Generation may take time depending on computer performance and Minecraft version. If the game freezes or lags, run the placement functions manually in smaller groups or increase the delay between scheduled function calls.

## Data Note

The full astronomical datasets may be too large to include directly in the repository. Sample data is included to demonstrate the workflow. The source code can be adapted to process larger Gaia, Hipparcos, or HYG datasets if the user provides the appropriate catalog files.

## Academic / Technical Purpose

This project was developed as an independent technical visualization project. It combines astronomy data, coordinate mathematics, Python scripting, and game-engine visualization to create an interactive 3D representation of nearby star systems. Although the final visualization is rendered in Minecraft, the core work is a data-processing and scientific visualization pipeline.

## For Reviewers

This project is included as an example of independent programming, technical problem-solving, and data visualization work. It shows the ability to take real-world scientific data, clean and transform it, generate structured outputs, and build a usable visualization pipeline.
