from collections import Counter


class TextService:

    @staticmethod
    def write(target, lines_it):
        counter = Counter()
        with open(target, "w") as o:
            for line in lines_it:
                o.write(line + "\n")
                counter["total"] += 1

        print("Saved: {}".format(target))
        print("Rows written: {}".format(counter["total"]))

