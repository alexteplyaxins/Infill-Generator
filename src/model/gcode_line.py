# -*- coding: utf-8 -*-
"""
Created on Thu Dec 17 13:20:35 2020

@author: hydre
"""

class gcode_line():
    def __init__(self):
        self.X = 0
        self.Y = 0
        self.Z = 0
        self.code = ''
        self.F = -1 # Lượng chạy dao
        self.S = -1 # Tốc độ đùn
        self.TE = -1 # Nhiệt độ 
        self.T = -1 # Đầu in
        self.M = -1 # Lệnh phụ
        self.G = -1 # Lệnh dịch chuyển
        self.R = -1 # Bán kính
        self.I = -1 # Nội suy G02
        self.J = -1 # Nội suy G02
        self.E = -1 # Extrusion volume in marlin

    def set(self, line):
        self.X = line.X
        self.Y = line.Y
        self.Z = line.Z
        self.R = line.R
        self.code = line.code
        self.F = line.F # Lượng chạy dao
        self.S = line.S # Tốc độ đùn
        self.TE = line.TE # Nhiệt độ 
        self.T = line.T # Đầu in
        self.M = line.M # Lệnh phụ
        self.G = line.G # Lệnh dịch chuyển
        self.I = line.I
        self.J = line.J
    def getGcodeline(self, line):
        try:
            cmd = ''
            num = "0"
            comment = False
            for c in line:
               # print('c:' + c)
                if c == ';':
                    break
                if c == '(':
                    comment = True
                if comment == False:
                    # print ('c: ' + c)
                    if c.isalpha():
                       # print('c isalpha:'+c)
                        if cmd != '\0':
                            # print('num0:' + num)
                            if num != '-' and num != '':
                                self.parseGCodeToken(cmd, float(num))
                        cmd = c
                        num = "0"
                    elif c.isnumeric() or c == '.' or c == '-':
                        if c== '-':
                            num = '-'
                        else:  
                            num += str(c)
                        
                        
                if c == ')':
                    comment = False
                if cmd != '\0':
                    if num!= '-' and num != '':
                        if '..' not in num:
                            self.parseGCodeToken(cmd, float(num))

        except Exception as bug:
            print(bug)
        
    def parseGCodeToken(self, cmd, value):
        if cmd =='T':
            self.T = int(value)
        elif cmd == 'F':
            self.F = value    
        elif cmd == 'G':
            self.G = int(value)    
        elif cmd =='X':
            self.X = value
        elif cmd == 'Y':
            self.Y = value
        elif cmd == 'Z':
            self.Z = value
        elif cmd == 'R':
            self.R = value
        elif cmd == 'I':
            self.I = value
        elif cmd == 'J':
            self.J = value
    
        