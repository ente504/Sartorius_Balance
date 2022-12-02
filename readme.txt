The Software is intended for the use at the IPF Dresden as an import tool of taken weightings on Sartorius Balances
(like the Sartorius Secura Lineup) to the Symate Detact System via MQTT.

This Software can be configured throw an config.ini file located in the root folder of the application.
An actual version is located at GitHub:

https://github.com/ente504/Sartorius_Balance/tree/master


Configuration of the Balance:
The Balance needs to be connected to the computer that runs the Import Software via a USB connection.
After connection the Balance to the computer the USB Interface can be configured in the Balanceses
Settings Menu. It needs to be configured as Keyboard in Table format.


Configuration of the Software:
in the following the needed configuration Keys ar described:

    DeviceName:
    Name of the Device. This must correspond to the machine name of the Device in the Detact System.

    ReadmePath:
    Path where to find this readme file

    Broker:
    IP Adress or Hoastname of the Detact MQTT Broker. The Detact MQTT Broker is at 172.20.115.125

    Port:
    Needed Port for the MQTT connection. The Port for the Detact Broker is 1883.

    UserName:
    Authentication Username for the MQTT connerction. (Detact)

    PassKey:
    Authentication Pasword for the MQTT connection (detact#1234)

    BaseTopic:
    Topic under which the Data is published to the Broker. (probekoerper)
