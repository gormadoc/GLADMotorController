# MCode considerations
	The receive buffer for an MCode device is 64 characters. If the length is exceeded CR/LF will occur and set error 20.

# MCode commands
	A (acceleration)
		Range: 91-1525878997 steps or 91-61035160 encoder counts
	AL
	AF
	AS
	AT
	BD (BAUD)
		Values: 48, 96, 19, 38, 11
	BP
	BR
	BY
	C1
	C2
	CA
	CB
	CC
	CE
	CF
	CK
	CL
	CM
	CP
	CR
	CT
	CW
	D (deceleration)
		Range: 91-1525878997 steps or 91-61035160 encoder counts
	D1-D4
	D5
	D9-D12
	DB
	DC
	DE
	DG
	DN
	E
	EE (encoder enable)
		Values: 0 (disable/default), 1 (enable)
	EF (error flag)
		Set high when there has been an error; to clear the flag ER must be read or set to 0
		Values: 0 (no error), 1 (error)
	EL
	EM (echo mode)
		Values: 0 (echo all/default), 1 (echo prompt), 2 (respond only to PR and L), 3 (save echo in printe queue)
	ER (error)
		Holds code of most recent error
	ES
	EX
	FC
	FD
	FM
	FT
	H (hold)
		Suspends program execution. If no value is given the program will be suspended while motion continues. A value in milliseconds can be given.
		Range: 1-65000
	HC
	HI
	HM
	HT
	I1-I4
	I5
	I6
	I7, I8
	I9-I12
	I13
	IC
	IF
	IL
	IH
	IN
	IP
	IT
	IV
	JE
	L
	LB
	LD
	LG
	LL
	LK
	LM
	LR
	LT
	MA (move to absolution position)
		Moves to an absolute postion (in steps). Takes 2.5 msec to calculate move. Sets MD to MA.
		Parameter 1: position
		Parameter 2 (optional): 0 (nothing extra/default), 1 (device name sent on completion)
		Parameter 3 (optional): 0 (nothing extra/default), 1 (motor will continue moving after reaching position)
	MD (motion mode)
		Returns the last motion command. Other 
	MF
	MP (moving to position)
		MP=1 when axis is moving to a position via MA or MR until MT.
	MR (move to relative position)
		Moves to a relative position (in steps). Takes 2.5 msec to calculate move. Sets MD to MR.
		Parameter 1: relative position
		Parameter 2 (optional): 0 (nothing extra/default), 1 (device name sent on completion)
		Parameter 3 (optional): 0 (nothing extra/default), 1 (motor will continue moving after reaching position)
	MS (Microstep resolution select)
		Dictates the microstep resolution. Consult the MCode manual for specifics as there are 20 settings.
	MT (Motor settling delay time)
		Allows motor to settle for MT milliseconds following a move, leaving MV high until the time is over.
		Range 0 (default) - 65000
	MU
	MV (moving flag)
		MV=1 while motion is occuring, MV=0 otherwise.
	NE (numeric enable)
		If NE=1, a user can enter in only a value and it will execute the previous motion command with that value.
	O1-O4
	O9-O12
	OE (on error handler)
	OL
	OH
	OT
	P (position counter)
		Represents the position counter in steps from C1 or encoder counts from C2. We will not change P as that would change the reference point of the system.
	PC
	PG
	PM
	PN (part number)
	PR (print)
		Sends text/data over serial to host.
	PS
	PW
	PY
	QD
	R1-R4
	RC
	RS
	RT
	S
	S1-S4, S9-S12
	S5
	S7, S8
	S13
	SC (start calibration)
	SF
	SL
	SM
	SN (serial number)
	SS
	ST
	SU
	TA
	TC
	TD (torque direction)
		Values: 0 (minus/CCW facing shaft), 1 (plus/CW facing shaft/default)
	TE
	TI
	TP
	TQ
	TR
	TS
	TT
	UG
	UV
	V (read velocity)
		Holds current velocity of the axis.
	VA
	VC
	VF
	VI (initial velocity)
		Initial velocity in steps or encoder counts per second following a move command.
		Range: 1 - VM-1; 1000/40 default
	VM (maximum velocity)
		Maximum velocity in steps or encoder counts per second that the axis can reach during a move.
		Range: VI+1 - 50000000 (steps), VI+1 - 2000000 (counts); 768000/30720 default
	VR (firmware version)
	WT

# MotorController interface
	# Common parameters
	* <motor> is either `m1` or `m2`
	* <parameter> is either `position` or `rate`
	* <time> is either `over` or `for` - Not implemented yet

	# Commands
	* get
		Returns parameter value at that time
		Usage: get <motor> <parameter>
	* set
		Issues command to set parameter value
		Usage 1: set <motor> <parameter> <value>
		Usage 2: set <motor> <parameter> <value> <time> <value>
	* hold
		Holds further motion until motion is complete
		Usage: hold <motor>