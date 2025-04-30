from course import Course
from constants import GRAY, RED, BLUE, GREEN, YELLOW, PURPLE

class CourseFactory:
    @staticmethod
    def create_all_courses():
        return [
            CourseFactory.create_easy_course(),
            CourseFactory.create_medium_course(),
            CourseFactory.create_hard_course(),
            CourseFactory.create_extreme_course()
        ]
    
    @staticmethod
    def create_easy_course():
        return Course(
            name="Easy Course",
            background_color=GRAY,
            player_config={
                "size": 60, 
                "color": BLUE, 
                "speed": 1
            },
            obstacle_configs={
                "spawn_rate": 120,
                "difficulty_increase_rate": 0.001,
                "max_difficulty": 1.3,
                "types": [
                    {"size": 60, "color": RED, "speed": 4, "shape": "rect"},
                    {"size": 60, "color": YELLOW, "speed": 4, "shape": "rect", "obstacle_type": "jump"},
                    {"size": 60, "color": PURPLE, "speed": 4, "shape": "rect", "obstacle_type": "duck"}
                ]
            }
        )
    
    @staticmethod
    def create_medium_course():
        return Course(
            name="Medium Course",
            background_color=(80, 80, 100),
            player_config={
                "size": 50, 
                "color": GREEN, 
                "speed": 1
            },
            obstacle_configs={
                "spawn_rate": 100,
                "difficulty_increase_rate": 0.002,
                "max_difficulty": 1.5,
                "types": [
                    {"size": 60, "color": RED, "speed": 6, "shape": "rect"},
                    {"size": 50, "color": YELLOW, "speed": 7, "shape": "circle"},
                    {"size": 60, "color": YELLOW, "speed": 6, "shape": "rect", "obstacle_type": "jump"},
                    {"size": 60, "color": PURPLE, "speed": 6, "shape": "rect", "obstacle_type": "duck"}
                ]
            }
        )
    
    @staticmethod
    def create_hard_course():
        return Course(
            name="Hard Course",
            background_color=(100, 50, 50),
            player_config={
                "size": 40, 
                "color": PURPLE, 
                "speed": 1
            },
            obstacle_configs={
                "spawn_rate": 80,
                "difficulty_increase_rate": 0.003,
                "max_difficulty": 1.7,
                "types": [
                    {"size": 60, "color": RED, "speed": 8, "shape": "rect"},
                    {"size": 50, "color": YELLOW, "speed": 9, "shape": "circle"},
                    {"size": 55, "color": GREEN, "speed": 10, "shape": "triangle"},
                    {"size": 60, "color": YELLOW, "speed": 8, "shape": "rect", "obstacle_type": "jump"},
                    {"size": 60, "color": PURPLE, "speed": 8, "shape": "rect", "obstacle_type": "duck"}
                ]
            }
        )
        
    @staticmethod
    def create_extreme_course():
        return Course(
            name="Extreme Course",
            background_color=(20, 20, 50),
            player_config={
                "size": 30, 
                "color": YELLOW, 
                "speed": 1
            },
            obstacle_configs={
                "spawn_rate": 60,
                "difficulty_increase_rate": 0.004,
                "max_difficulty": 2.0,
                "types": [
                    {"size": 65, "color": RED, "speed": 12, "shape": "rect"},
                    {"size": 55, "color": YELLOW, "speed": 13, "shape": "circle"},
                    {"size": 45, "color": GREEN, "speed": 14, "shape": "triangle"},
                    # Special fast obstacle with smaller hitbox
                    {"size": 30, "color": PURPLE, "speed": 16, "shape": "circle"},
                    {"size": 65, "color": YELLOW, "speed": 12, "shape": "rect", "obstacle_type": "jump"},
                    {"size": 65, "color": PURPLE, "speed": 12, "shape": "rect", "obstacle_type": "duck"}
                ]
            }
        ) 