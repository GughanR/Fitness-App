class WorkoutPlan:
    def __init__(self, **kwargs):
        self.workout_plan_id = kwargs["workout_plan_id"]
        self.workout_plan_name = kwargs["workout_plan_name"]
        self.workout_plan_type = kwargs["workout_plan_type"]
        self.workout_plan_goal = kwargs["workout_plan_goal"]
        self.workout_list = kwargs["workout_list"]
        self.last_workout = kwargs["last_workout"]

def check_plan_type(plan_type, muscles_chosen):
    # Set muscle groups
    push_muscles = ["chest", "triceps", "shoulders"]
    pull_muscles = ["back", "biceps", "forearms"]
    leg_muscles = ["quadriceps", "glutes", "hamstrings", "calves"]

    if plan_type == "push pull legs":
        muscle_groups = [push_muscles, pull_muscles, leg_muscles]
    elif plan_type == "upper lower":
        muscle_groups = [push_muscles + pull_muscles, leg_muscles]
    else:
        muscle_groups = [push_muscles+pull_muscles+leg_muscles]
    
    # Check that at least one muscle from each group is in chosen muscles
    all_valid = True
    for muscle_group in muscle_groups:
        group_valid = False
        for muscle in muscle_group:
            if muscle in muscles_chosen:
                group_valid = True
        if group_valid == False:
            all_valid = False

    return all_valid



def create_workout_plan(plan_goal, muscles_chosen, plan_type, plan_name):
    # Check that plan type and muscles compatible
    check_plan_type(plan_type, muscles_chosen)


if __name__ == "__main__":
    mc = ["chest", "biceps", "hamstrings"]
    print(check_plan_type("push pull legs", mc))