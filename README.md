<p align="center">
  <a href="" rel="noopener">
 <img width=200px height=200px src="logo.png" alt="Project logo"></a>
</p>

<h3 align="center">healthy-py</h3>

---

<p align="center"> Analyze the health data from "all the things" in one place using Python, Docker, and Metabase.
    <br> 
</p>

## 📝 Table of Contents

- [About](#about)
- [Dataflow](#dataflow)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting_started)
- [Usage](#usage)
- [TODO](#todo)

## 🧐 About <a name = "about"></a>

This is a full stack BI application powered by Python, Docker, and Metabase. It is designed to be a one stop shop for analyzing all of your health data from all of your favorite sources:

### Supported Data Sources

- ⌚ [Apple Health Data](https://www.apple.com/ios/health/)
- 🏋️ [Strong App](https://www.strong.app/)

### Dataflow Diagram <a name = "dataflow"></a>

```mermaid
flowchart LR

    subgraph Sources
        A[Apple Health export<br>XML, ECG CSV, GPX]
        B[Strong App export<br>strong.csv]
    end

    subgraph LocalData
        D[Local data directory<br>data/apple_health_export<br>data/strong_export]
    end

    subgraph Pipeline
        E[Extract and transform<br>datapipelines/extract.py]
        F[Load to Postgres<br>datapipelines/load.py<br>db/synchronous.py]
    end

    subgraph Warehouse
        G[(PostGIS database<br>Docker container)]
    end

    subgraph MetabaseStack
        H[(Metabase backend DB)]
        I[Metabase app<br>Dashboards and questions]
        J[Init scripts<br>init-metabase]
    end

    U[User (browser)]

    A --> D
    B --> D
    D --> E
    E --> F
    F --> G
    G --> I
    J --> H
    J --> I
    H --> I
    U --> I
```

### Roadmap Data Sources

There are many more data sources that I would like to add to this app. If you have any suggestions, please open an issue or a pull request!

## 🔒 Prerequisites <a name = "prerequisites"></a>

Docker ([Docker Desktop comes with Docker](https://www.docker.com/products/docker-desktop/))


## 🏁 Getting Started <a name = "getting_started"></a>

### Getting the data

Export your Apple Watch's health data from the Health app on your iPhone. 

Open the Health app:
Click **Profile** (profile picture right corner) ⇨ **Export All Health Data**. This will create a zip file with all of your health data. Unzip this file.

Export your Strong App data by going to the Strong app, clicking on **Profile** ⇨ **Settings** ⇨ **Export Strong Data**. This will create a `.csv` file with all of your Strong data. 

Get these files onto the computer that you are running the app on (I usually AirDrop them to my Mac).

### Adding the data to the appropriate directories

Clone the repoisitory
```
git clone https://github.com/nathanjones4323/healthy-py.git
```

Navigate to the app's directory
```
cd healthy-py
```

Create a `data` directory in the root of the app
```
mkdir data
```

Add your Apple Watch's health data (the entire folder) and Strong App exports to the `data` directory.

At this point your `data` directory should look like this:

```
data
├── apple_health_export
│   ├── electrocardiograms
│   │   ├── ecg_2023-09-05.csv
│   │   ├── ...
│   │   └── ecg_2023-09-06.csv
│   ├── export.xml
│   ├── export_cda.xml
│   └── workout-routes
│       ├── route_2023-09-05_8.40pm.gpx
│       ├── ...
│       └── route_2023-09-08_7.20pm.gpx
└── strong_export
    └── strong.csv
```

### Creating and populating the .env files

Create an `.env` file in each of these directories:

```zsh
healthy-py/db
healthy-py/metabase
healthy-py/metabase/backend
```

By running the following commands inside of the root directory:

```zsh
mkdir db && touch db/.env
mkdir metabase && touch metabase/.env
mkdir metabase/backend && touch metabase/backend/.env
```

Fill in the following values in the `.env` files:

`healthy-py/db/.env` - These will be the values you input inside of the Metabase UI when you create an admin user and connect to the database.

```zsh
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=
POSTGRES_PORT=
```

`healthy-py/metabase/.env` - These values will be automaticaly identified and used by Metabase when you run the container to set up the Metabase instance

```zsh
MB_DB_TYPE=
MB_DB_DBNAME=
MB_DB_PORT=5432
MB_DB_USER=
MB_DB_PASS=
MB_DB_HOST=metabase-backend
# Admin User Credentials
MB_ADMIN_EMAIL=
MB_ADMIN_PASSWORD=
```

`healthy-py/metabase/backend/.env` - These values will be automaticaly identified and used by Metabase when you run the container to initialize a user for the Metabase backend

```zsh
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=
```

## 🏃 Usage <a name = "usage"></a>

Navigate to the app's directory
```
cd healthy-py
```

Start the container and seed the database with your health data

```
docker-compose -f docker-compose.yml up -d
```

If this is your first time running the app, you'll have to wait ~30 seconds for Metabase to start before accessing http://localhost:3000/.

If the page is not loading, wait a few more seconds and refresh. Once you see the Metabase set up page, you can proceed to set up your admin user and connect to the database.

> :warning: You must use values from the `metabase/.env` file and `db/.env` file when setting up the admin user and connecting to the database.

You should use the following values when setting up the admin user:

```
# Admin User Credentials
MB_ADMIN_EMAIL
MB_ADMIN_PASSWORD

# Database Credentials
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_DB
POSTGRES_PORT
```

After you have set up the admin user and connected to the database, you will see that all of the automatic analysis (Metabase collections, questions, and dashboards) has been added. (This process takes ~5 minutes, you can check the status of the process by inspecting the logs of the `init-metabase-questions` container)

Stop the container

```
docker-compose -f docker-compose.yml down
```

> :warning: If you need to rebuild and run the container run this command

```
docker-compose up --force-recreate --build -d && docker image prune -f
```

## 📓 TODO <a name = "todo"></a>

*TODOs are in order of priority*

* Need to update this step from `questions.py`
```python
# Add the field filters to the payload (template-tags)
  my_custom_json = add_field_filters(
      mappings=field_mappings, my_custom_json=my_custom_json)
```
To handle the `[[ and reps >= {{min_reps}} ]]` min max filters. Right now it is only set up for field filters

* Update the **Getting Started** section of the README with all of the steps to get the app running and initialized
* Add Apple Health Questions
  * Sleep
    * Sleep Time - What time do I fall asleep?
    * Wake Time - What time do I wake up?
    * Duration - How long do I sleep?
    * Sleep by stage - How much time do I spend in each sleep stage?
    * Average/Median Sleep Time - What is my average/median sleep time?
  
  * Activity
    * Calories - How many calories do I burn?
      * Resting Calories - How many calories do I burn while resting?
      * Active Calories - How many calories do I burn while active?
    * Steps - How many steps do I take?
    * Distance - How far do I walk?
    * Flights Climbed - How many flights of stairs do I climb?
    * Exercise Time - How much time do I spend exercising?
    * Stand Time - How much time do I spend standing?
    * V02 Max - What is my V02 Max?
  
  * Heart Rate
    * Max Heart Rate - What is my max heart rate?
    * Resting Heart Rate - What is my resting heart rate?
    * Average/Median Heart Rate - What is my average/median heart rate?
    * Heart Rate Variability - What is my heart rate variability?
    * Heart Rate by Activity - What is my heart rate during different activities?

  * Workouts
    * Workout Time - How much time do I spend working out?
    * Workout Type - What types of workouts do I do?
    * Workout Intensity - How intense are my workouts?
    * Workout by Activity - How much time do I spend doing different activities?
    * Workout by Intensity - How much time do I spend doing different intensities?
    * Workout by Type - How much time do I spend doing different types of workouts?
    * Workout by Heart Rate - How much time do I spend in different heart rate zones?
    * Workout by Distance - How much time do I spend traveling different distances?
    * Workout by Calories - How much time do I spend burning different amounts of calories?
    * Workout by Steps - How much time do I spend taking different amounts of steps?
    * Workout by Flights Climbed - How much time do I spend climbing different amounts of flights?
    * Workout by Elevation - How much time do I spend at different elevations?
    * Workout by Pace - How much time do I spend at different paces?
    * Workout by Cadence - How much time do I spend at different cadences?
    * Workout by Heart Rate Variability - How much time do I spend at different heart rate variabilities?
    * Workout by Heart Rate - How much time do I spend at different heart rates?
    * Workout by Heart Rate Zone - How much time do I spend at different heart rate zones?
    * Workout by Heart Rate Zone and Type - How much time do I spend at different heart rate zones for different types of workouts?
    * Workout by Heart Rate Zone and Intensity - How much time do I spend at different heart rate zones for different intensities?
    * Workout by Heart Rate Zone and Distance - How much time do I spend at different heart rate zones for different distances?
    * Workout by Heart Rate Zone and Calories - How much time do I spend at different heart rate zones for different calories?
    * Workout by Heart Rate Zone and Steps - How much time do I spend at different heart rate zones for different steps?
    * Workout by Heart Rate Zone and Flights Climbed - How much time do I spend at different heart rate zones for different flights climbed?
    * Workout by Heart Rate Zone and Elevation - How much time do I spend at different heart rate zones for different elevations?
    * Workout by Heart Rate Zone and Pace - How much time do I spend at different

  * Research and brainstorm more questions

* Create a dashboard with all of the questions ==> [Link to API documentation to automate adding questions to dashboards](https://www.metabase.com/docs/latest/api/dashboard#put-apidashboardid)
* Make the start of the `init-metabase-questions` container wait using `docker-compose.yml` instead of using `time.sleep` with the `auth` function inside of `metabase-api/init/auth.py`
* Make `is_initialized` function inside of `metabase-api/init/auth.py` check for each question's existence before skipping the full initialization process. This will let updates to the initialization process be applied after the initial run.
* For the API to work, the Metabase admin must be logged in. This is not ideal. Need to find a way to authenticate the API calls without doing setup through the GUI.
* Find a dynamic way to set the values for
  * graph.x_axis.title_text
  * graph.y_axis.title_text
  * graph.dimensions
  * graph.metrics