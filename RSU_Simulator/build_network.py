

import os

def create_network():
    nodes_content = """<nodes>
    <node id="center" x="0.0" y="0.0" type="traffic_light"/>
    <node id="top" x="0.0" y="150.0"/>
    <node id="bottom" x="0.0" y="-150.0"/>
    <node id="left" x="-150.0" y="0.0"/>
    <node id="right" x="150.0" y="0.0"/>
</nodes>"""

    with open("intersection.nod.xml", "w") as f:
        f.write(nodes_content)

    edges_content = """<edges>
    <edge id="L_to_C" from="left" to="center" numLanes="2" speed="11.11"/>
    <edge id="C_to_R" from="center" to="right" numLanes="2" speed="11.11"/>
    <edge id="R_to_C" from="right" to="center" numLanes="2" speed="11.11"/>
    <edge id="C_to_L" from="center" to="left" numLanes="2" speed="11.11"/>
    <edge id="T_to_C" from="top" to="center" numLanes="2" speed="11.11"/>
    <edge id="C_to_B" from="center" to="bottom" numLanes="2" speed="11.11"/>
    <edge id="B_to_C" from="bottom" to="center" numLanes="2" speed="11.11"/>
    <edge id="C_to_T" from="center" to="top" numLanes="2" speed="11.11"/>
</edges>"""

    with open("intersection.edg.xml", "w") as f:
        f.write(edges_content)

    os.system("netconvert --node-files=intersection.nod.xml --edge-files=intersection.edg.xml --output-file=intersection.net.xml")

    print("Network generated (150m).")

if __name__ == "__main__":
    create_network()


def create_rsus():
    
    content = '<additional>\n'
    
    inbound_edges = ["L_to_C", "R_to_C", "T_to_C", "B_to_C"]
    
    for edge in inbound_edges:
        

        content += f'    <inductionLoop id="RSU_{edge}_Start_L0" lane="{edge}_0" pos="5" freq="1" file="out.xml"/>\n'
        content += f'    <inductionLoop id="RSU_{edge}_Start_L1" lane="{edge}_1" pos="5" freq="1" file="out.xml"/>\n'
        
        
        content += f'    <inductionLoop id="RSU_{edge}_End_L0" lane="{edge}_0" pos="130" freq="1" file="out.xml"/>\n'
        content += f'    <inductionLoop id="RSU_{edge}_End_L1" lane="{edge}_1" pos="130" freq="1" file="out.xml"/>\n'

    content += '</additional>'
    
    with open("intersection.add.xml", "w") as f:
        f.write(content)
    
    print("RSU detectors generated.")

if __name__ == "__main__":
    create_rsus()

import random

def generate_routefile():
    random.seed(42)

    with open("intersection.rou.xml", "w") as routes:
        print("""<routes>
    <vType id="car" accel="2.6" decel="4.5" sigma="0.5" length="5" minGap="2.5" maxSpeed="11.11" guiShape="passenger"/>
    """, file=routes)

        directions = ["L", "R", "T", "B"]
        veh_id = 0

        def choose_direction(start):
            # 60% straight
            if random.random() < 0.6:
                return directions[(directions.index(start)+2)%4]
            else:
                return random.choice([d for d in directions if d != start])

        # Low traffic
        for t in range(0, 60, 6):
            start = random.choice(directions)
            end = choose_direction(start)

            print(f'    <trip id="veh{veh_id}" type="car" depart="{t}" from="{start}_to_C" to="C_to_{end}"/>', file=routes)
            veh_id += 1

        # Medium traffic
        for t in range(60, 120, 3):
            start = random.choice(directions)
            end = choose_direction(start)

            print(f'    <trip id="veh{veh_id}" type="car" depart="{t}" from="{start}_to_C" to="C_to_{end}"/>', file=routes)
            veh_id += 1

        # High traffic
        for t in range(120, 180, 1):
            start = random.choice(directions)
            end = choose_direction(start)

            print(f'    <trip id="veh{veh_id}" type="car" depart="{t}" from="{start}_to_C" to="C_to_{end}"/>', file=routes)
            veh_id += 1

        print("</routes>", file=routes)

    print("Routes generated.")

if __name__ == "__main__":
    generate_routefile()

def create_sumo_config():
    config_content = """<configuration>
    <input>
        <net-file value="intersection.net.xml"/>
        <route-files value="intersection.rou.xml"/>
        <additional-files value="intersection.add.xml"/>
    </input>
    <time>
        <begin value="0"/>
        <end value="3600"/>
    </time>
</configuration>""" 
    with open("intersection.sumocfg", "w") as f:
        f.write(config_content)
    
    print("Success: 'intersection.sumocfg' updated without view settings.")

if __name__ == "__main__":
    create_sumo_config()

