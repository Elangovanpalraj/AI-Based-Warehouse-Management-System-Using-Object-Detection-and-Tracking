# simple_tracker.py

class SimpleTracker:
    def __init__(self):
        self.center_points = {}
        self.id_count = 0

    def update(self, objects_rect):
        objects_bbs_ids = []
        new_center_points = {}

        for rect in objects_rect:
            x1, y1, x2, y2 = rect
            cx = int((x1 + x2) / 2)
            cy = int((y1 + y2) / 2)

            same_object_detected = False
            for id, pt in self.center_points.items():
                dist = ((cx - pt[0])**2 + (cy - pt[1])**2)**0.5
                if dist < 30:
                    new_center_points[id] = (cx, cy)
                    objects_bbs_ids.append([x1, y1, x2, y2, id])
                    same_object_detected = True
                    break

            if not same_object_detected:
                new_center_points[self.id_count] = (cx, cy)
                objects_bbs_ids.append([x1, y1, x2, y2, self.id_count])
                self.id_count += 1

        self.center_points = new_center_points.copy()
        return objects_bbs_ids
