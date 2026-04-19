### Cloud-based temperature, humidity, and rain warning system

A comprehensive IoT system that simulates the collection of environmental data (temperature, humidity, rainfall) from virtual sensors on Proteus, processes the data via Arduino, transmits it to the Cloud ThingsBoard, and displays it in real time on the control panel.

### First Step:
1. Proteus 8 profesional and necessary libraries
2. Arduino IDE
3. Thingboards
4. Python
5. Virtual Serial Port Driver (VSPD)

### System Run Steps
# Step 1: Open Proteus
Open the file Temperature_Rain_Monitoring.pdsprj

Check the connections (compare with the diagram in the Appendix)

# Step 2: Load the HEX file into Arduino
Open Arduino IDE, load the file Temperature_Rain_Monitoring.ino

Select Sketch → Export Compiled Binary (Ctrl+Alt+S)

Copy the newly created .hex file to the project folder

In Proteus, double-click on Arduino → Program File → select the .hex file(include in this project)

# Step 3: Virtual COM configuration
chưa làm chưa biết

# Step 4: Run Python Bridge
chịu hello world!