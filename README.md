# Incentive Systems for Fleets of New Mobility Services
<p align="center">
<img src="https://github.com/ghafeleb/Incentive_Systems_for_New_Mobility_Services/blob/main/images/incentiveOfferingPlatforms.png" width="100%" alt="Traditional vs. Organization Incentivization"/>
  <br>
  <em>(a) Traditional platforms for offering incentives: incentives are offered to individual drivers in the system. (b) Presented platform for offering incentives: incentives are offered to new mobility services to change their drivers' behavior.</em>
</p>

<p align="justify">
Traffic congestion has become an inevitable challenge in large cities due to population increases and the expansion of urban areas. Various approaches are introduced to mitigate traffic issues, encompassing from expanding the road infrastructure to employing demand management. Congestion pricing and incentive schemes are extensively studied for traffic control in traditional networks where each driver/rider is a network "player." In this setup, drivers'/riders' "selfish" behavior hinders the network from reaching a socially optimal state. In future mobility services, on the other hand, a large portion of drivers/vehicles may be controlled by a small number of companies/organizations. In such a system, offering incentives to organizations can potentially be much more effective in reducing traffic congestion rather than offering incentives directly to drivers. This paper studies the problem of offering incentives to organizations to change the behavior of their individual drivers (or individuals relying on the organization’s services). We developed a model where incentives are offered to each organization based on the aggregated travel time loss across all drivers/riders in that organization. Such an incentive offering mechanism requires solving a large-scale optimization problem to minimize the system-level travel time. We propose an efficient algorithm for solving this optimization problem. Numerous experiments on Los Angeles County traffic data reveal the ability of our method to reduce system-level travel time by up to 7.15%. Moreover, our experiments show that incentivizing organizations can be up to 7 times more cost-effective than incentivizing individual drivers when aiming for maximum travel time reduction.
</p>

<p align="justify">
Our framework will be based on the following three-step procedure:
  
Step 1) The central planner receives organizations’ demand estimates for the next time interval (e.g., the next few hours).

Step 2) The central planner incentivizes organizations to change their routes and travel time.

Step 3) Observe organizations’ response and go back to Step 1 for the next time interval.

The central planner (which is referred to as "Incentive OfferingPlatform" in Fig. 1 (b)) continually repeats this three-step process in the network for every time interval. A detailed description of the process is provided in the following figure:
</p>

<p align="center">
<img src="https://github.com/ghafeleb/Incentive_Systems_for_New_Mobility_Services/blob/main/images/incentivization_cycle_noBack.PNG" width="40%" alt="Incentivization Steps"/>
  <br>
  <em>Detailed description of the incentivization process.</em>
</p>


# Dependencies
<p align="justify">
  The required packages must be installed via Anaconda or pip before running the codes. Download and install <b>Python 2.x version</b> from  <a href="https://www.python.org/downloads/">Python 2.x Version</a>. You can install the required packages via pip using the following command:
</p>

```
python2 -m pip install -r python2_requirements.txt
```

<p align="justify">
Download and install <b>Python 3.x version</b> from <a href="https://www.python.org/downloads/">Python 3.x Version</a>.  You can install the required packages via pip using the following command:
</p>

```
python3 -m pip install -r python3_requirements.txt
```

<p align="justify">
Moreover, you must install MATLAB before running the scripts in this repository. You can download and install MATLAB from <a href="https://www.mathworks.com/">MathWorks website</a>. Next, you should install CVX by following the steps provided on <a href="https://cvxr.com/cvx/doc/install.html">CVX website</a>. Next, you should <a href="https://cvxr.com/cvx/doc/gurobi.html">install the Gurobi solver on CVX</a>.
</p>

# Data
<p align="justify">
We evaluate our incentive scheme's effectiveness using Los Angeles area data. The presence of multiple routes between most origin-destination (OD) pairs makes the Los Angeles area particularly suitable for our assessment. We use the data collected by the Archived Data Management System (ADMS), a comprehensive transportation dataset compilation by University of Southern California researchers. First, we extract sensor details, including their locations. We extract the speed and volume data of selected sensors. Nodes for the network graph are chosen from on-ramps and highway intersections. Connecting link data is derived from in-between sensors. Node distances are determined via Google Maps API. The data preparation workflow is as follows:
</p>

<p align="center">
  <img src="https://github.com/ghafeleb/Incentive_Systems_for_New_Mobility_Services/blob/main/images/data_preparation_workflow.png" width="40%" alt="Data Preparation Workflow"/>
  <br>
  <em>Data preparation workflow: First, traffic data and sensors' location data are received from ADMS Server. Next, sensors' location data is processed to compute sensor distances. Finally, sensor distances and traffic data are combined to create the graph network data.</em>
</p>

<p align="justify">
Our network encompasses highways around Downtown Los Angeles and has 12 nodes, 32 links, 288.1 miles of road, 144 OD pairs, and 270 paths between OD pairs.

<p align="center">
  <img src="https://github.com/ghafeleb/Incentive_Systems_for_New_Mobility_Services/blob/main/images/region_y3_new.PNG" width="75%" />
  <br>
  <em>Studied region and the highway sensors inside the region. This region encompasses several areas notorious for high traffic congestion, particularly Downtown Los Angeles.</em>
<p align="center">

<p align="justify">
The Los Angeles County data cannot be shared with the public, but synthetic data is provided in the demo to check the code. 
</p>

# Demo
<p align="justify">
You can test the incentivization on a synthetic graph network by running the following command:
</p>

```
cd scripts
python runDemo.py --region_ "region_toy" --config_filename "../data/YAML/region_toy.yaml" --n_iter_UE 5 --seed_data 2 --seed_solver 2 --budget 10000 --VOT 2.63 --solver_name "ADMM" --MIPGap 0.01 --n_iter_ADMM 100 --step_size_UE 0.01 --percNonUVal 50 --nPath 2 --n_time 204 --n_time_inc_start 13 --n_time_inc_end 24 --rho 20 --n_companies_ADMM 1
```

<p align="justify">
First, the demo creates the synthetic data as a demo example. The demo graph includes 4 nodes (O, A, B, and D) and one Origin-Destination (OD) pair: node O as the origin and node D as the destination. There are 4 roads/edges (x, y, z, and w) with 2 routes between the OD (route 1: x-y, route 2: z-w). After creating the data, the demo incentivizes the system's user drivers. Finally, it computes the incentivization cost.
</p>

<p align="center">
  <img src="https://github.com/ghafeleb/Incentive_Systems_for_New_Mobility_Services/blob/main/images/synthetic_data.png" width="40%" alt="Demo Graph"/>
  <br>
  <em>Demo graph.</em>
<p align="center">

# Origin-Destination (OD) Estimation
For OD estimation, we rely on the code from <a href="https://github.com/ghafeleb/Congestion-Reduction-via-Personalized-Incentives/tree/main">Congestion Reduction via Personalized Incentives paper repo</a> which is an adapted and modified version of the <a href="https://github.com/Lemma1/DPFE">implementation of dynamic origin-destination demand estimation</a>.

  
# Numerical Experiments
## Traffic Reduction Analysis
<p align="justify">
We analyze the traffic reduction as a decrease in the system's travel time. The following plot provides the percentage of travel time decrease with incentivization as compared to a system with no incentivization at VOT of $157.8 for different penetration rates (percentage of drivers to which the incentivization platform is able to incentivize). The budget of $0 shows the case of a no-incentivization. The no-incentivization system solution assumes all drivers are background drivers. We observe that by increasing the available budget, the decrease in travel time increases (as expected). This decrease is more for the same budgets at larger penetration rates because the model has access to more drivers to select and has more flexibility to recommend alternative routes. The plot shows up to <b>7% travel time reduction</b> using the incentivization platform.
</p>

<p align="center">
  <img src="https://github.com/ghafeleb/Incentive_Systems_for_New_Mobility_Services/blob/main/images/ttReductionPerc_VOT2.63_solvADMM_percNonU95_90_85_80.png" width="40%" />
<p align="center">
  

## Incentivization Cost Analysis
<p align="justify">
The number of organizations in the system can alter the total travel time and cost. The following figure illustrates the percentage decrease in travel time and total cost when there are different numbers of organizations in the system. As an extreme case, we also include the case that each organization contains one driver (i.e., we incentivize individuals rather than organizations). In the following figure, we observe a higher cost for reducing the same amount of travel time when more organizations are in the system. The intuitive reason behind this observation is as follows. For each organization, some drivers lose time after incentivization and some gain travel time. At the organizational level, the time changes of drivers can cancel each other out. Hence, we may not need to compensate the organization significantly. When the number of drivers per organization decreases, the canceling effect becomes weaker, and the incentivization costs more. This also explains why incentivizing organizations is much more cost-efficient than incentivizing individual drivers. 
</p>

<p align="center">
  <img src="https://github.com/ghafeleb/Incentive_Systems_for_New_Mobility_Services/blob/main/images/costTTReduction_VOT2.63_solvADMM_percNonU95.png" width="40%" />
<p align="center">

## Algorithm Performance Analysis
<p align="justify">
We compare our presented algorithm against Gurobi and MOSEK as state-of-the-art commercial solvers. Our algorithm 
</p>

* Achieves speeds up to **12 times faster** than Gurobi and **120 times faster** than MOSEK

<p align="center">
  <img src="https://github.com/ghafeleb/Incentive_Systems_for_New_Mobility_Services/blob/main/images/execTimeComparison_percNonU95_90_85_80.png" alt="Gutobi vs. ADMM Execution Time Comparison" width="40%"/>
<p align="center">
  
* Closely mirrors the performance of Gurobi and Mosek 
<p align="center">
  <img src="https://github.com/ghafeleb/Incentive_Systems_for_New_Mobility_Services/blob/main/images/ttReductionPerc_VOT2.63_solvADMM_Gurobi_percNonU95_90_85_80.png" alt="Gutobi vs. ADMM Travel Time Reduction Comparison" width="40%"/>
<p align="center">
  
* **Saves up to $5000** in incentivization cost  
<p align="center">
  <img src="https://github.com/ghafeleb/Incentive_Systems_for_New_Mobility_Services/blob/main/images/costComparisonVOT_VOT2.63_solv1Gurobi_solv2ADMM_percNonU95_90_85_80_nC1.png" alt="Gutobi vs. ADMM Incentivization Cost Comparison" width="40%"/>
<p align="center">


## Citation

If you find this repository useful in your research, please cite the following paper:
```
@article{ghafelebashi2023incentive,
  title={Incentive Systems for Fleets of New Mobility Services},
  author={Ghafelebashi, Ali and Razaviyayn, Meisam and Dessouky, Maged},
  journal={arXiv preprint arXiv:2312.02341},
  year={2023}
}
```
