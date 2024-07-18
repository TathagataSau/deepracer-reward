import math

def reward_function(params):
    '''
    In @params object:

    {
        "all_wheels_on_track": Boolean,    # flag to indicate if the vehicle is on the track
        "x": float,                        # vehicle's x-coordinate in meters
        "y": float,                        # vehicle's y-coordinate in meters
        "distance_from_center": float,     # distance in meters from the track center 
        "is_left_of_center": Boolean,      # Flag to indicate if the vehicle is on the left side to the track center or not. 
        "heading": float,                  # vehicle's yaw in degrees
        "progress": float,                 # percentage of track completed
        "steps": int,                      # number steps completed
        "speed": float,                    # vehicle's speed in meters per second (m/s)
        "steering_angle": float,           # vehicle's steering angle in degrees
        "track_width": float,              # width of the track
        "waypoints": [[float, float], … ], # list of [x,y] as milestones along the track center
        "closest_waypoints": [int, int]    # indices of the two nearest waypoints.
    }
    '''

    #################
    ### Constants ###
    #################

    MAX_REWARD = 1e2
    MIN_REWARD = 1e-3
    DIRECTION_THRESHOLD = 10.0
    ABS_STEERING_THRESHOLD = 30

    ########################
    ### Input parameters ###
    ########################

    on_track = params['all_wheels_on_track']
    distance_from_center = params['distance_from_center']
    track_width = params['track_width']
    steering = abs(params['steering_angle'])  # Only need the absolute steering angle for calculations
    speed = params['speed']
    waypoints = params['waypoints']
    closest_waypoints = params['closest_waypoints']
    heading = params['heading']
    progress = params['progress']

    ########################
    ### Helper functions ###
    ########################

    def on_track_reward(current_reward, on_track):
        if not on_track:
            current_reward = MIN_REWARD
        else:
            current_reward = MAX_REWARD
        return current_reward

    def distance_from_center_reward(current_reward, track_width, distance_from_center):
        # Calculate 3 marks that are farther and father away from the center line
        marker_1 = 0.1 * track_width
        marker_2 = 0.25 * track_width
        marker_3 = 0.5 * track_width

        # Give higher reward if the car is closer to center line and vice versa
        if distance_from_center <= marker_1:
            current_reward *= 1.2
        elif distance_from_center <= marker_2:
            current_reward *= 0.8
        elif distance_from_center <= marker_3:
            current_reward += 0.5
        else:
            current_reward = MIN_REWARD  # likely crashed/ close to off track

        return current_reward

    def steering_reward(current_reward, steering):
        # Penalize reward proportionally to the steering angle
        penalty = abs(steering) / 30  # Adjust 30 based on your steering range
        current_reward *= (1 - penalty)
        return current_reward

    def throttle_reward(current_reward, speed, steering):
        # Decrease throttle while steering to promote smoother driving
        if abs(steering) > 0:
            max_speed = 2.5 - (0.4 * abs(steering))
            if speed > max_speed:
                current_reward *= max_speed / speed
        return current_reward

    def progress_reward(current_reward, progress):
        # Reward for making progress on the track
        current_reward += progress * 0.1  # Adjust 0.1 based on desired reward per % progress
        return current_reward

    def direction_reward(current_reward, waypoints, closest_waypoints, heading):
        '''
        Calculate the direction of the center line based on the closest waypoints    
        '''
        next_point = waypoints[closest_waypoints[1]]
        prev_point = waypoints[closest_waypoints[0]]

        # Calculate the direction in radians, arctan2(dy, dx), the result is (-pi, pi)
        direction = math.atan2(next_point[1] - prev_point[1], next_point[0] - prev_point[0])
        # Convert to degrees
        direction = math.degrees(direction)

        # Calculate difference between track direction and car heading angle
        direction_diff = abs(direction - heading)

        # Penalize if the difference is too large
        if direction_diff > DIRECTION_THRESHOLD:
            current_reward *= 0.5

        return current_reward

    def curve_reward(current_reward, waypoints, closest_waypoints, heading):
        # Adjust reward based on the curvature of the track ahead
        next_point = waypoints[closest_waypoints[1]]
        prev_point = waypoints[closest_waypoints[0]]
        track_curve = math.atan2(next_point[1] - prev_point[1], next_point[0] - prev_point[0])
        heading_diff = abs(track_curve - heading)
        if heading_diff < 10:
            current_reward *= 1.1
        elif heading_diff > 30:
            current_reward *= 0.8
        return current_reward

    ########################
    ### Execute Rewards  ###
    ########################

    reward = 1.0  # Start with a base reward

    reward = on_track_reward(reward, on_track)
    reward = distance_from_center_reward(reward, track_width, distance_from_center)
    reward = steering_reward(reward, steering)
    reward = throttle_reward(reward, speed, steering)
    reward = progress_reward(reward, progress)
    reward = direction_reward(reward, waypoints, closest_waypoints, heading)
    reward = curve_reward(reward, waypoints, closest_waypoints, heading)

    return float(reward)
