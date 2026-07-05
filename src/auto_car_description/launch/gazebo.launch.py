import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess, DeclareLaunchArgument, SetEnvironmentVariable
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    pkg = get_package_share_directory('auto_car_description')
    urdf_file = os.path.join(pkg, 'urdf', 'auto_car.urdf')

    with open(urdf_file, 'r') as f:
        robot_description = f.read()

    world_arg = DeclareLaunchArgument(
        'world',
        default_value='empty.sdf',
        description='World file name (e.g. empty.sdf, l_shaped.sdf, obstacle_room.sdf, multi_room.sdf)'
    )

    world_file = [os.path.join(pkg, 'worlds', ''), LaunchConfiguration('world')]

    resource_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=os.path.join(pkg, '..')
    )

    return LaunchDescription([
        resource_path,
        world_arg,
        ExecuteProcess(
            cmd=['gz', 'sim', world_file],
            output='screen'
        ),
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_description}]
        ),
        Node(
            package='ros_gz_sim',
            executable='create',
            arguments=['-name', 'auto_car', '-topic', 'robot_description', '-x', '-2.0', '-y', '-2.0', '-z', '0.1'],
            output='screen'
        ),
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=[
                '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
                '/odom@nav_msgs/msg/Odometry@gz.msgs.Odometry',
                '/clock@rosgraph_msgs/msg/Clock@gz.msgs.Clock',
                '/scan@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan',
                '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
                '/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model',
            ],
            output='screen'
        ),
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            arguments=['0', '0', '0', '0', '0', '0',
                       'lidar_link',
                       'auto_car/base_footprint/lidar'],
            output='screen'
        ),
    ])
