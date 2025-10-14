angular_velocity = 12.49119882 # [rad/s]
wheel_radius = 37/2/1000 # [m]

cases = [[1,1,1,1], [-1,-1,-1,-1], [1,-1,-1,1], [-1,1,1,-1]] # FL 0 // FR 1 // RL 2 // RR 3

for case in cases:
    vx, vy = (angular_velocity*case[0]+angular_velocity*case[1]+angular_velocity*case[2]+angular_velocity*case[3])*wheel_radius/4, (-angular_velocity*case[0]+angular_velocity*case[1]+angular_velocity*case[2]-angular_velocity*case[3])*wheel_radius/4

    print(f"Case {case}:{" "*(19-len(str(case)))}Vx = {"{:+.10f}".format(vx)} [m/s o mm/ms]   Vy = {"{:+.10f}".format(vy)} [m/s o mm/ms]")