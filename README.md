# GLADMotorController
For controlling a GLAD system motor controller.

# Packages needed:
I use Anaconda with Python 3.8.5
  * PySerial
  * PyQt5
  * os
  * sys
  * time

# Other software
For debugging I've used com0com to setup virtual COM ports `COM8` (program side) and `COM9` (virtual motor controller). It may be necessary to use a specific version of com0com (see issue here: https://sourceforge.net/p/com0com/bugs/32/); I used version 2.2.2.0 and renamed the default virtual ports. I have not added anything to do this without user intervention yet.
  
# Goals
The software packaged with the MC was just a text terminal for entering in machine commands over serial. 
It is easy to enter incorrect commands when controlling in real-time and scripting is somewhat arcane, while calculating correct values based on the current step and microstep resolution is unnecessary busy work that lends itself well to error.
This project is intended to entirely replace as much of that software as possible and to make scripting easy, as well as to extend it with commonly used functionality and scheduling. This can also be easily interfaced with other programs to 

# Considerations
Motor one controls the rotation of the sample and motor two controls the tilt. As such, motor two is constrained between 0 and 90 degrees for useful behavior. The actual calculations behind the positions and rotations are hidden behind the backend. The only access the end-user has to these is through the microstep resolution, which shouldn't need to be controlled often.

# Current status
 * All scripting is line-by-line, working similar to the terminal interface with more readability and error checking.
 * Scripts cannot be saved or loaded (copy-paste works in the box though).
 * Scheduling is in a preliminary state.
 * Not all controller commands are implemented; it might never be necessary to include more.
 * Step resolution cannot currently be controlled; perhaps it will never be.
