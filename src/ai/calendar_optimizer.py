from datetime import timedelta


class CalendarOptimizer:
    """
    Responsible for intelligently placing tasks
    into available schedule slots.

    Goals:
    - Reduce overload
    - Prevent burnout
    - Prioritize deep work
    - Avoid schedule conflicts
    - Spread difficult tasks intelligently
    """
    def __init__(self):
        pass

    # =========================================================
    # MAIN ENTRY
    # =========================================================

    def optimize_schedule(
        self,
        tasks,
        available_blocks,
        behavior_profile=None
    ):
        """
        Assigns tasks into calendar blocks.

        Parameters:
        - tasks:
            list of AI-enhanced tasks

        - available_blocks:
            free calendar slots

        - behavior_profile:
            user productivity patterns
        """

        """
        Assigns tasks into calendar blocks.

        Parameters:
        - tasks:
            list of AI-enhanced tasks

        - available_blocks:
            free calendar slots

        - behavior_profile:
            user productivity patterns
        """

        optimized_schedule = []

        # Highest priority first
        tasks = sorted(
            tasks,
            key=lambda t: t.ai_priority,
            reverse=True
        )

        for task in tasks:

            best_block = self.find_best_block(
                task,
                available_blocks,
                behavior_profile
            )

            if best_block:

                schedule_item = {
                    "task": task,
                    "start": best_block["start"],
                    "end": best_block["start"] + timedelta(
                        hours=task.predicted_duration
                    )
                }

                optimized_schedule.append(schedule_item)

                # Shrink remaining block
                best_block["start"] += timedelta(
                    hours=task.predicted_duration
                )

        return optimized_schedule
# =========================================================
    # FIND BEST BLOCK
    # =========================================================

    def find_best_block(
        self,
        task,
        available_blocks,
        behavior_profile
    ):

        valid_blocks = []

        for block in available_blocks:

            duration = (
                block["end"] - block["start"]
            ).total_seconds() / 3600

            if duration >= task.predicted_duration:
                valid_blocks.append(block)

        if not valid_blocks:
            return None

        scored_blocks = []

        for block in valid_blocks:

            score = self.score_block(
                task,
                block,
                behavior_profile
            )

            scored_blocks.append((score, block))

        scored_blocks.sort(
            key=lambda x: x[0],
            reverse=True
        )

        return scored_blocks[0][1]
# =========================================================

        # =====================================================
        # MORNING FOCUS BONUS
        # =====================================================

        if behavior_profile:

            preferred_hours = (
                behavior_profile.get(
                    "preferred_focus_hours",
                    []
                )
            )

            if start_hour in preferred_hours:
                score += 25

        # =====================================================
        # HARD TASK EARLIER BONUS
        # =====================================================

        if getattr(task, "difficulty", 1) >= 7:

            if start_hour < 15:
                score += 15

        # =====================================================
        # AVOID LATE NIGHT WORK
        # =====================================================

        if start_hour >= 22:
            score -= 30

        # =====================================================
        # DEADLINE URGENCY
        # =====================================================

        if getattr(task, "hours_until_deadline", 999) < 24:
            score += 20

        return score
 # =========================================================
    # BURNOUT CHECK
    # =========================================================

    def detect_overload(self, schedule):

        total_hours = 0

        for item in schedule:

            duration = (
                item["end"] - item["start"]
            ).total_seconds() / 3600

            total_hours += duration

        # Example threshold
        if total_hours > 10:
            return True

        return False

    # =========================================================
    # INSERT BREAKS
    # =========================================================

    def insert_breaks(self, schedule):

        updated = []

        for i, item in enumerate(schedule):

            updated.append(item)

            duration = (
                item["end"] - item["start"]
            ).total_seconds() / 3600

            if duration >= 2:

                break_item = {
                    "task": "BREAK",
                    "start": item["end"],
                    "end": item["end"] + timedelta(
                        minutes=15
                    )
                }

                updated.append(break_item)

        return updated