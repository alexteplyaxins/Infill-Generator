import math
import enum

class MODE_CREATE(enum.Enum):
    INTERNAL = 0
    SIDE = 1
    GRADIENT = 2

def cos(angle):
    if angle % 180 == 90:
        return 0
    elif angle % 180 == 0:
        return 1
    else:
        return math.cos(angle*math.pi/180)


def sin(angle):
    return math.sin(angle*math.pi/180)


class ParallelEdges:
    def __init__(self, listPts, pos=0):
        self.listPts = listPts
        self.updatePointPosition(pos)
        self.parallelEdges = []
        self.generateParallelEdges()

    def generateParallelEdges(self):
        self.parallelEdges = []
        self.parallelEdges.append([[self.listPts[0], self.listPts[1]], [
                                  self.listPts[1], self.listPts[2]]])
        self.parallelEdges.append([[self.listPts[3], self.listPts[2]], [
                                  self.listPts[2], self.listPts[1]]])
        self.parallelEdges.append([[self.listPts[4], self.listPts[3]], [
                                  self.listPts[3], self.listPts[2]]])
        self.parallelEdges.append([[self.listPts[4], self.listPts[5]], [
                                  self.listPts[5], self.listPts[0]]])

    def updatePointPosition(self, pos):
        for i in range(0, len(self.listPts)):
            p = list(self.listPts[i])
            p[0] += pos[0]
            p[1] += pos[1]
            self.listPts[i] = tuple(p)


class HoneyCombTri:
    def __init__(self, rect, density, ewidth, pos=[0, 0], angle=0):
        if density <= 0.0:
            return []
        if density > 1.0:
            density = 1.0
        distance = ewidth / density
        d = distance / cos(30)
        min_x, min_y, max_x, max_y = rect
        self.NrEdges = 6
        self.xmin = min_x
        self.xmax = max_x
        self.ymin = min_y
        self.ymax = max_y
        self.width = self.xmax - self.xmin
        self.height = self.ymax - self.ymin
        self.d = d
        self.ListPoints = []
        self.ListEdges = []
        self.ListParallelEdges = []
        # self.ZoneMatrix = []
        self.Matrix = []
        self.Results = []
        self.NrCellX = 0
        self.NrCellY = 0
        self.CreateZone()
        self.CreateCell()
        self.modeInternal(pos)
        # self.MultipleXY()
        # self.Generate()

    def GenerateEdges(self, pos, sideLength=0, startPt=None, mode=0):
        if mode == MODE_CREATE.INTERNAL.value:
            self.modeInternal(pos)

    def modeInternal(self, pos):
        angleAutoUp = 360 / self.NrEdges
        curAngle = -30
        radiant = self.d
        center = self.Center
        firstPoint = (round(center[0] + radiant * cos(curAngle), 3),
                      round(center[1] + radiant * sin(curAngle), 3))
        self.ListPoints.append(firstPoint)
        for i in range(1, self.NrEdges):
            curAngle += angleAutoUp
            point = (round(center[0] + cos(curAngle) * radiant, 3),
                     round(center[1] + sin(curAngle) * radiant, 3))
            self.ListPoints.append(point)
        for i in range(0, self.NrEdges):
            j = i + 1
            if j == self.NrEdges:
                j = 0
            self.ListEdges.append([self.ListPoints[i], self.ListPoints[j]])
        self.ListParallelEdges = ParallelEdges(
            self.ListPoints, pos).parallelEdges

    def MultipleXY(self):

        # self.MultipleType1()
        # self.MultipleType2()
        self.MultipleType3()

    def CreateZone(self):
        self.ZoneXmin = self.xmin
        self.ZoneXmax = self.xmax
        self.ZoneYmin = self.ymin
        self.ZoneYmax = self.ymax
        self.ZoneRootPoint = (self.ZoneXmin, self.ZoneYmin)

    def CreateCell(self):
        self.CellX = self.d * sin(60) * 2
        self.CellY = self.d * 2 * 1.5
        self.NrCellX = int((self.ZoneXmax-self.ZoneXmin) / self.CellX) + 1
        self.NrCellY = int((self.ZoneYmax-self.ZoneYmin) / self.CellY) + 1
        self.Center = (self.ZoneRootPoint[0] + self.d * sin(60),
                       self.ZoneRootPoint[1] + self.d)

    def CheckValid(self, line):
        if line[1][0] < self.ZoneXmin or line[1][0] > self.ZoneXmax:
            return False
        if line[1][1] < self.ZoneYmin or line[1][1] > self.ZoneYmax:
            return False
        return True

    def MultipleType1(self):
        type1 = self.ListParallelEdges[0]
        type1M = []
        loop = 0
        while 1:
            index = 1
            edges = self.CreateCopy(type1, loop)

            if self.CheckValid(edges[0]):
                type1M.append([])
                type1M[-1].append(edges[0])
            else:
                break
            if self.CheckValid(edges[1]):
                type1M[-1].append(edges[1])
            else:
                break
            while 1:
                demo = self.CreateConnect(edges, index, 1)

                if self.CheckValid(demo[0]):
                    type1M[-1].append(demo[0])
                else:
                    break
                if self.CheckValid(demo[1]):
                    type1M[-1].append(demo[1])
                else:
                    break
                index += 1
            loop += 1
        loop = 1
        while 1:
            index = 1
            edges = self.CreateCopy(type1, self.NrCellX-2, loop)
            if self.CheckValid(edges[0]):
                type1M.append([])
                type1M[-1].append(edges[0])
            else:
                break
            if self.CheckValid(edges[1]):
                type1M[-1].append(edges[1])
            else:
                break
            while 1:
                demo = self.CreateConnect(edges, index, 1)
                if self.CheckValid(demo[0]):
                    type1M[-1].append(demo[0])
                else:
                    break
                if self.CheckValid(demo[1]):
                    type1M[-1].append(demo[1])
                else:
                    break
                index += 1
            loop += 1
        self.Matrix.append(type1M)

    def MultipleType2(self):
        type1 = self.ListParallelEdges[1]
        type2 = self.ListParallelEdges[3]
        type1M = []
        for i in range(0, self.NrCellY):
            index = 1
            edges = self.CreateCopy(type2, j=i)
            type1M.append(edges)
            for j in range(1, self.NrCellX):
                demo = self.CreateConnect(edges, index, 1)
                if demo[1][1][0] < self.ZoneXmin or demo[1][1][0] > self.ZoneXmax:
                    break
                if demo[1][1][1] < self.ZoneYmin or demo[1][1][1] > self.ZoneYmax:
                    break
                type1M[-1].append(demo[0])
                type1M[-1].append(demo[1])
                index += 1
            index = 1
            edges = self.CreateCopy(type1, j=i)
            type1M.append(edges)
            for j in range(1, self.NrCellX):
                demo = self.CreateConnect(edges, index, 1)
                if demo[1][1][0] < self.ZoneXmin or demo[1][1][0] > self.ZoneXmax:
                    break
                if demo[1][1][1] < self.ZoneYmin or demo[1][1][1] > self.ZoneYmax:
                    break
                type1M[-1].append(demo[0])
                type1M[-1].append(demo[1])
                index += 1

        self.Matrix.append(type1M)

    def MultipleType3(self):
        type1 = self.ListParallelEdges[2]
        type1M = []
        for i in range(0, self.NrCellX):
            index = 1
            edges = self.CreateCopy(type1, i)
            type1M.append(edges)
            while 1:
                demo = self.CreateConnect(edges, index, 1)
                if demo[1][1][0] < self.ZoneXmin or demo[1][1][0] > self.ZoneXmax:
                    break
                if demo[1][1][1] < self.ZoneYmin or demo[1][1][1] > self.ZoneYmax:
                    break
                type1M[-1].append(demo[0])
                type1M[-1].append(demo[1])
                index += 1
        for i in range(1, self.NrCellY):
            index = 1
            edges = self.CreateCopy(type1, 0, i)
            type1M.insert(0, edges)
            while 1:
                demo = self.CreateConnect(edges, index, 1)
                if demo[1][1][0] < self.ZoneXmin or demo[1][1][0] > self.ZoneXmax:
                    break
                if demo[1][1][1] < self.ZoneYmin or demo[1][1][1] > self.ZoneYmax:
                    break
                type1M[0].append(demo[0])
                type1M[0].append(demo[1])
                index += 1
        self.Matrix.append(type1M)

    def CreateCopy(self, edges, i=0, j=0):
        line1 = [list(edges[0][0]), list(edges[0][1])]
        line2 = [list(edges[1][0]), list(edges[1][1])]
        if i > 0:
            line1[0][0] = round(line1[0][0] + i*self.CellX, 3)
            line1[1][0] = round(line1[1][0] + i*self.CellX, 3)
            line2[0][0] = round(line2[0][0] + i*self.CellX, 3)
            line2[1][0] = round(line2[1][0] + i*self.CellX, 3)
        if j > 0:
            line1[0][1] = round(line1[0][1] + j*self.CellY, 3)
            line1[1][1] = round(line1[1][1] + j*self.CellY, 3)
            line2[0][1] = round(line2[0][1] + j*self.CellY, 3)
            line2[1][1] = round(line2[1][1] + j*self.CellY, 3)
        return [line1, line2]

    def CreateConnect(self, edges, i=0, value=1):
        line1 = [list(edges[0][0]), list(edges[0][1])]
        line2 = [list(edges[1][0]), list(edges[1][1])]
        disx = round(edges[1][1][0] - edges[1][0][0] +
                     edges[0][1][0] - edges[0][0][0], 3)
        disy = round(edges[1][1][1] - edges[1][0][1] +
                     edges[0][1][1] - edges[0][0][1], 3)
        if i > 0:
            line1[0] = (edges[0][0][0] + value*i*disx,
                        edges[0][0][1] + value*i*disy)
            line1[1] = (edges[0][1][0] + value*i*disx,
                        edges[0][1][1] + value*i*disy)
            line2[0] = (edges[1][0][0] + value*i*disx,
                        edges[1][0][1] + value*i*disy)
            line2[1] = (edges[1][1][0] + value*i*disx,
                        edges[1][1][1] + value*i*disy)
        return [line1, line2]

    def CheckParallel(self, Line, Connection):
        v1 = [round(Line[1][0] - Line[0][0], 2),
              round(Line[1][1] - Line[0][1], 2)]  # vtpt của pt1
        # pt2: là pt cắt
        v2 = [round(Connection[1][0] - Connection[0][0], 2), round(Connection[1]
              [1] - Connection[0][1], 2)]  # vtpt của pt1
        if (v1[0] == 0 and v2[0] == 0) or (v1[1] == 0 and v2[1] == 0):
            return True
        if round((v1[0]*v2[0] + v1[1]*v2[1]) / (math.sqrt(v1[0]**2+v2[0]**2) * math.sqrt((v1[1]**2+v2[1]**2))), 3) == 1:
            return True
        elif round((v1[0]*v2[0] + v1[1]*v2[1]) / (math.sqrt(v1[0]**2+v2[0]**2) * math.sqrt((v1[1]**2+v2[1]**2))), 3) == -1:
            return True

        else:
            return False


    def Generate(self):
        for Type in self.Matrix:
            Lines = []
            reverse = True
            for lines in Type:
                data = []
                if reverse is False:
                    if len(Lines) > 0:
                        valid = self.CheckParallel(
                            Lines[-1], [Lines[-1][1], lines[0][0]])
                        if valid is True:
                            Lines.pop(-1)
                        valid2 = self.CheckParallel(
                            lines[0], [Lines[-1][1], lines[0][0]])
                        if valid2 is True:
                            lines.pop(0)
                        try: # Dont know why it will be failed in d=3
                            Lines.append([Lines[-1][1], lines[0][0]])
                        except:
                            continue
                    for line in lines:
                        Lines.append(line)
                    reverse = True
                else:
                    for i in range(len(lines)-1, -1, -1):
                        data.append([lines[i][1], lines[i][0]])
                    if len(Lines) > 0:
                        valid = self.CheckParallel(
                            Lines[-1], [Lines[-1][1], data[0][0]])
                        if valid is True:
                            Lines.pop(-1)
                        valid2 = self.CheckParallel(
                            data[0], [Lines[-1][1], data[0][0]])
                        if valid2 is True:
                            data.pop(0)
                        Lines.append([Lines[-1][1], data[0][0]])
                    for line in data:
                        Lines.append(line)
                    reverse = False
            self.Results.append(Lines)

    def visualize(self):
        import matplotlib.pyplot as plt

        for result in self.Results:
            x_values = []
            y_values = []

            for line in result:
                x_values.extend([pt[0] for pt in line])
                y_values.extend([pt[1] for pt in line])

            plt.plot(x_values, y_values, 'b-')

        plt.gca().set_aspect('equal', adjustable='box')
        plt.show()

    def generate_layer_1(self):
        self.Matrix.clear()
        self.MultipleType1()
        self.Generate()
        results = self.convert_output()
        # Remove Result for this layer
        self.Results.clear()
        return results

    def generate_layer_2(self):
        self.Matrix.clear()
        self.MultipleType2()
        self.Generate()
        results = self.convert_output()
        # Remove Result for this layer
        self.Results.clear()
        return results

    def generate_layer_3(self):
        self.Matrix.clear()
        self.MultipleType3()
        self.Generate()
        results = self.convert_output()
        # Remove Result for this layer
        self.Results.clear()
        return results

    def convert_output(self):
        final_results = []
        count = 0
        for line in self.Results[0]:
            newline = []
            for pt in line:
                newline.append(tuple(pt))
            final_results.append(newline)
        return final_results

    def print_final_results(self, results):
        count = 0
        print(results)
        for line in results:
            print(f"line #{count} is: {line}")
            count += 1

if __name__ == "__main__":
    # min_x, min_y, max_x, max_y
    rect = [83.373, 75.505, 124.847, 126.403]
    # honeycomb = HoneyComb(xmin=83.373, xmax=124.847, ymin=75.505, ymax=126.403, d=3)
    honeycomb = HoneyComb(rect, d=3)
    # honeycomb.visualize()
    # result = honeycomb.get_edges()
    layer1 = honeycomb.generate_layer_1()
    print(layer1)
    layer2 = honeycomb.generate_layer_2()
    print(layer2)
    layer3 = honeycomb.generate_layer_3()
    print(layer3)

