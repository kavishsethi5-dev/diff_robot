## ROS2 Compatibility Note

### gz_bridge.yaml — Pose Topic Name

The topic name for the pose publisher differs between ROS2 Jazzy and Rolling 
due to a change in  `gz-sim-pose-publisher-system` plugin

- **Jazzy (24.04):** The plugin publishes on `/model/my_robot/pose`
- **Rolling (24.04):** The plugin publishes on `my_robot/pose`

In `config/gz_bridge.yaml`,:

**Jazzy:**
```yaml
- ros_topic_name: "/model/my_robot/pose"
  gz_topic_name: "/model/my_robot/pose"
  ros_type_name: "geometry_msgs/msg/Pose"
  gz_type_name: "gz.msgs.Pose"
  direction: GZ_TO_ROS
```

**Rolling:**
```yaml
- ros_topic_name: "my_robot/pose"
  gz_topic_name: "my_robot/pose"
  ros_type_name: "geometry_msgs/msg/Pose"
  gz_type_name: "gz.msgs.Pose"
  direction: GZ_TO_ROS
```
