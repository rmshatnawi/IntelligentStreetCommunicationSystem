import os
import random

SPEED_LIMIT = 11.11  # 40 km/h

# Generate many unique plate numbers so cars keep appearing longer
PLATE_NUMBERS = [f"CAR-{i:03d}" for i in range(1, 121)]

# Add stolen vehicles from Firebase
PLATE_NUMBERS[18] = "STL-999"
PLATE_NUMBERS[55] = "STL-555"


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

    edges_content = f"""<edges>
    <edge id="L_to_C" from="left" to="center" numLanes="1" speed="{SPEED_LIMIT}"/>
    <edge id="C_to_R" from="center" to="right" numLanes="1" speed="{SPEED_LIMIT}"/>
    <edge id="R_to_C" from="right" to="center" numLanes="1" speed="{SPEED_LIMIT}"/>
    <edge id="C_to_L" from="center" to="left" numLanes="1" speed="{SPEED_LIMIT}"/>
    <edge id="T_to_C" from="top" to="center" numLanes="1" speed="{SPEED_LIMIT}"/>
    <edge id="C_to_B" from="center" to="bottom" numLanes="1" speed="{SPEED_LIMIT}"/>
    <edge id="B_to_C" from="bottom" to="center" numLanes="1" speed="{SPEED_LIMIT}"/>
    <edge id="C_to_T" from="center" to="top" numLanes="1" speed="{SPEED_LIMIT}"/>
</edges>"""

    with open("intersection.edg.xml", "w") as f:
        f.write(edges_content)

    os.system(
        "netconvert --node-files=intersection.nod.xml "
        "--edge-files=intersection.edg.xml "
        "--output-file=intersection.net.xml"
    )

    print("Network generated.")


def create_rsus():
    content = """<additional>

    <inductionLoop id="RSU_01_START" lane="L_to_C_0" pos="10" freq="1" file="out.xml"/>
    <inductionLoop id="RSU_01_END"   lane="L_to_C_0" pos="130" freq="1" file="out.xml"/>

    <inductionLoop id="RSU_02_START" lane="R_to_C_0" pos="10" freq="1" file="out.xml"/>
    <inductionLoop id="RSU_02_END"   lane="R_to_C_0" pos="130" freq="1" file="out.xml"/>

    <inductionLoop id="RSU_03_START" lane="T_to_C_0" pos="10" freq="1" file="out.xml"/>
    <inductionLoop id="RSU_03_END"   lane="T_to_C_0" pos="130" freq="1" file="out.xml"/>

    <inductionLoop id="RSU_04_START" lane="B_to_C_0" pos="10" freq="1" file="out.xml"/>
    <inductionLoop id="RSU_04_END"   lane="B_to_C_0" pos="130" freq="1" file="out.xml"/>

</additional>"""

    with open("intersection.add.xml", "w") as f:
        f.write(content)

    print("8 RSUs generated: START and END for each segment.")


def generate_routefile():
    random.seed(42)

    with open("intersection.rou.xml", "w") as routes:
        print(f"""<routes>
    <vType id="car"
           accel="2.6"
           decel="4.5"
           sigma="0.5"
           length="5"
           minGap="2.5"
           maxSpeed="{SPEED_LIMIT}"
           guiShape="passenger"/>
""", file=routes)

        directions = ["L", "R", "T", "B"]

        def choose_direction(start):
            if random.random() < 0.6:
                return directions[(directions.index(start) + 2) % 4]
            return random.choice([d for d in directions if d != start])

        traffic_plan = [
            (0, 60, 8),      # Low traffic
            (60, 120, 5),    # Medium traffic
            (120, 240, 2),   # High traffic / congestion
            (240, 300, 4),   # Traffic easing
        ]

        veh_id = 0

        for start_time, end_time, step in traffic_plan:
            for t in range(start_time, end_time, step):
                if veh_id >= len(PLATE_NUMBERS):
                    break

                start = random.choice(directions)
                end = choose_direction(start)
                plate = PLATE_NUMBERS[veh_id]

                print(
                    f'    <trip id="{plate}" type="car" depart="{t}" '
                    f'from="{start}_to_C" to="C_to_{end}"/>',
                    file=routes
                )

                veh_id += 1

        print("</routes>", file=routes)

    print(f"Routes generated with {veh_id} unique plate numbers.")
    print("Stolen plates included: STL-999, STL-555")


def create_sumo_config():
    config_content = """<configuration>
    <input>
        <net-file value="intersection.net.xml"/>
        <route-files value="intersection.rou.xml"/>
        <additional-files value="intersection.add.xml"/>
    </input>
    <time>
        <begin value="0"/>
        <end value="500"/>
    </time>
</configuration>"""

    with open("intersection.sumocfg", "w") as f:
        f.write(config_content)

    print("SUMO config generated: intersection.sumocfg")


def main():
    create_network()
    create_rsus()
    generate_routefile()
    create_sumo_config()
    print("Done.")


if __name__ == "__main__":
    main()
