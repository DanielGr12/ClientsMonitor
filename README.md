# Clients Monitor
This Project is about monitoring a couple of computers computers at the same time.


First, A manager needs to login with his username and password, there can be more than one manager, each manager has different capabilities.
The password is saved as a salted and peppered hash, in addition to that, the hash is performed with argon2 alrorithm.
This algorithm is more safe than the other popular hashes because this algoritgm takes more time and more resources from the computer, because of that if the database is leaked the hacker will need more time to guess every hash and is will slow him down significantly.


The manager's main screen depends on the privilege level, each level has different options:

1. Level 1:
In this level the manager has only the option to toggle between the clients monitors(if they have more than one) and to only view the screens.

![level1Control](https://user-images.githubusercontent.com/87939329/221238744-b4822512-20a7-4ea1-b9f0-50edb14fd4a4.png)

2. Level 2:
In this level the manager also has the option to take a screenshot of the frame from the client.

![level2Control](https://user-images.githubusercontent.com/87939329/221240932-436ce403-56f1-46b7-829c-2c08d677b3c2.png)


3. Level 3:
In this level the manager more options including the options that were on the last levels:
A. Take control of the client's computer and the client's mouse and keyboard will be disabled.
B. Disconnect the client from the system.
C. Disable the client's mouse and keyboard.

![level3Control](https://user-images.githubusercontent.com/87939329/221240896-865e7326-56ea-499c-a248-88f59b94d712.png)

4. Level 4:
This level includes the option to duplicate files that exist on the client's computer.
The manager chooses what file he wants to copy and what will be the name of it on the manager's computer.
This transfer is encrypted with AES128 and with a digital signature(hmac algorithm) to ensure that the file came untampered from the client and no one changed it in the middle.

![level4Control](https://user-images.githubusercontent.com/87939329/221241493-d7f5697c-166a-41a1-b84b-8af1c6014580.png)


Only the managers with the highest level of permissions will be able to promote the managers with lower levels of permissions to the higher ones.
