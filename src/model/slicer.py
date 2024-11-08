# == slicer.py ==
#   written by Revar Desmera (2017/11)
#   extended by Rene K. Mueller (2021/04)

from __future__ import print_function

import re
import math
import time
import datetime
import random
import os.path

from appdirs import user_config_dir
from Infill.infillgenerator import InfillGenerator
from conf.config import slicer_configs
from utils.config_parser import load_printing_schedule
import model.geometry2d as geom

from PySide6.QtCore import Qt, Signal, QObject
from conf.config import CONFIG_FILE
from utils.config_parser import ConfigParser

############################################################
class Slicer(QObject):

    prog_bar_signal = Signal(int)
    
    def __init__(self, models, logger=None, prog_bar=None,
                 enable_perims=None, print_schedule=None,
                 **kwargs):
        
        super().__init__()
        
        self.models = models
        self.logger = logger
        self.prog_bar = prog_bar
        self.enable_perims = enable_perims
        self.conf = {}
        self.conf_metadata = {}
        
        self.config_parser = ConfigParser(logger=self.logger, conf=self.conf, conf_metadata=self.conf_metadata)
        self.config_parser.load_configs()
        self.last_pos = (0.0, 0.0, 0.0)
        self.last_e = 0.0
        self.last_nozl = -1 #Sua 231022
        self.total_build_time = 0.0
        self.mag = 4
        self.layer = 0
        self.last_typ = ''
        self.last_retract_typ = ''
        self.config(**kwargs)
        self.NAME = 'SUN3000'
        self.VERSION = '1'
        
        if print_schedule is None:
            self.print_plan = load_printing_schedule()
        else:
            self.print_plan = print_schedule
        
        self.raw_layer_paths = {}
        self.gcode_data = []

    def update_print_schedule(self, print_schedule):
        if not print_schedule:
            print("ERROR, Invalid print schedule")
            return
        self.print_plan = print_schedule

    def config(self, **kwargs):
        for key, val in kwargs.items():
            if key in self.conf:
                self.conf[key] = val

    def slice_to_file(self, filename=''):
        st = time.time()
        self.raw_layer_paths = {}
        
        if self.logger is not None:
            self.logger.info("Slicing @ {:.3f}mm layer height".format(self.conf['layer_height']))
        else:
            print("Slicing @ {:.3f}mm layer height".format(self.conf['layer_height']))
        self.dflt_nozl = self.conf['default_nozzle']
        self.infl_nozl = self.conf['infill_nozzle']

        self.center_point = (self.conf['bed_center_x'], self.conf['bed_center_y'])
        if self.infl_nozl == -1:
            self.infl_nozl = self.dflt_nozl
         # Dùng giá trị trong giao diện
        

         # Dùng giá trị trong config
        dflt_nozl_d = self.conf['nozzle_{0}_diam'.format(self.dflt_nozl)]
        infl_nozl_d = self.conf['nozzle_{0}_diam'.format(self.infl_nozl)]
        self.layer_h = self.conf['layer_height']
        #self.extrusion_ratio = 1.25  # -- ??? from where comes this number?
        self.extrusion_ratio = self.conf['nozzle_{0}_flow_rate'.format(self.infl_nozl)]
        self.extrusion_width = dflt_nozl_d * self.extrusion_ratio
        self.infill_width = infl_nozl_d * self.extrusion_ratio

        for model in self.models:
            # print("slicer model")
            # print(model)
            if self.conf['random_pos']:
                x = ((random.random() * 2) - 1) * (
                            self.conf['bed_size_x'] / 2 - (model.points.maxx - model.points.minx + 10) / 2)
                y = ((random.random() * 2) - 1) * (
                            self.conf['bed_size_y'] / 2 - (model.points.maxy - model.points.miny + 10) / 2)
                if self.logger is not None:
                    self.logger.info("Random offset {},{}".format(int(x), int(y)))
                else:
                    print("+ Random offset {},{}".format(int(x), int(y)))
                model.center((self.center_point[0] + int(x), self.center_point[1] + int(y),
                              (model.points.maxz - model.points.minz) / 2.0))
            else:
                model.center(
                    (self.center_point[0], self.center_point[1], (model.points.maxz - model.points.minz) / 2.0))
            model.assign_layers(self.layer_h)

        height = max([model.points.maxz - model.points.minz for model in self.models]) # Lỗi cắt lớp do self.models không có giá trị
        self.layers = int(height / self.layer_h)
        self.layer_zs = [
            self.layer_h * (layer + 1)
            for layer in range(self.layers)
        ]

        # gcode
        if self.logger is not None:
            self.logger.info("Start compute the object's perimeter")
        print("--> Perimeters computing")
        self._slicer_task_perimeters()
        if self.prog_bar is not None:
            # self.prog_bar.setValue(25)
            self.prog_bar_signal.emit(25)

        if self.logger is not None:
            self.logger.info("Start compute the object infill")
        print("--> Infill computing")
        self._slicer_task_fill()
        if self.prog_bar is not None:
            # self.prog_bar.setValue(50)
            self.prog_bar_signal.emit(50)

        if self.logger is not None:
            self.logger.info("Start compute the pathing for extruders")
        print("--> Pathing computing")
        self._slicer_task_pathing()
        if self.prog_bar is not None:
            self.prog_bar_signal.emit(75)

        if self.logger is not None:
            self.logger.info("Generate the GCode")
        print("--> Export GCode to \"{}\"".format(filename))
        self.gcode_data = self._slicer_task_gcode()
        if self.prog_bar is not None:
            self.prog_bar_signal.emit(100)

        if filename != '':
            self.write_gcode_to_file(self.gcode_data, filename)

        msg = "Took {:.02f}s total. Estimated build time: {:d}h {:02d}m, filament used: {:.03f}m, layers: {:d}".format(
                time.time() - st,
                int(self.total_build_time / 3600),
                int((self.total_build_time % 3600) / 60),
                self.last_e / 1000,
                self.layers
            )
        if self.logger is not None:
            self.logger.info(msg)
        else:
            print(msg)


    ###################################################################################################
    def _slicer_task_perimeters(self):
        self.layer_paths = []
        self.perimeter_paths = []
        self.skirt_bounds = []
        random_starts = self.conf['random_starts']
        self.dead_paths = []
        print("self.layers")
        print(self.layers)
        for layer in range(self.layers):
            # Layer Slicing
            z = self.layer_zs[layer]
            paths = []
            layer_dead_paths = []
            for model in self.models:
                model_paths, dead_paths = model.slice_at_z(z - self.layer_h / 2, self.layer_h)
                layer_dead_paths.extend(dead_paths)
                model_paths = geom.orient_paths(model_paths)
                paths = geom.union(paths, model_paths)
            self.layer_paths.append(paths)
            self.dead_paths.append(layer_dead_paths)

            # Perimeters
            perims = []
            randpos = random.random()
            for i in range(self.conf['shell_count']):
                # shell = geom.offset(paths, -( i + 0.5) * self.extrusion_width)
                shell = geom.offset(paths, -i * 0.5 * self.extrusion_width)
                shell = geom.close_paths(shell)
                if self.conf['random_starts']:
                    shell = [
                        (path if i == 0 else (path[i:] + path[1:i + 1]))
                        for path in shell
                        for i in [int(randpos * (len(path) - 1))]
                    ]
                perims.insert(0, shell)
            self.perimeter_paths.append(perims)

        self.top_masks = []
        self.bot_masks = []
        for layer in range(self.layers):
            # Top and Bottom masks
            below = [] if layer < 1 else self.perimeter_paths[layer - 1][0]
            perim = self.perimeter_paths[layer][0]
            above = [] if layer >= self.layers - 1 else self.perimeter_paths[layer + 1][0]
            self.top_masks.append(geom.diff(perim, above))
            self.bot_masks.append(geom.diff(perim, below))

    def _slicer_task_fill(self):
        self.solid_infill = []
        self.sparse_infill = {}

        self.infill_gen = InfillGenerator()
        for layer in range(self.layers):
            bounds, solid_mask, perims = self._slicer_gen_solid_mask(layer)

            # Solid Infill
            self._slicer_gen_solid_infill(solid_mask=solid_mask, bounds=bounds, layer_num=layer)
            self._slicer_infill_one_layer(layer=layer, solid_mask=solid_mask, perims=perims, bounds=bounds)

    def _slicer_infill_one_layer(self, layer, solid_mask, perims, bounds):
        sparse_infill = {}

        print_data = self.print_plan['layer_{0}'.format(layer % len(self.print_plan))]
        for nozzl, nozzl_data in print_data.items():
            pos = nozzl_data['pos']
            density = float(nozzl_data['density'])
            spacing = float(nozzl_data['spacing'])
            infill_type = nozzl_data['infill']

            if density > 0.0:
                if density >= 0.99:
                    infill_type = "Lines"
                mask = geom.offset(perims[0], self.conf['infill_overlap'] - self.infill_width)
                mask = geom.diff(mask, solid_mask)
                print("Bounding Box:{0}".format(bounds))
                lines = self.infill_gen.generate_infill(density=density, spacing = spacing, infill_type=infill_type,
                                                        bounds=bounds, layer_num=layer, pos=pos,
                                                        ewidth=self.infill_width)
                lines = geom.clip(lines, mask, subj_closed=False)
                
                # Convert from 1-base to 0-base
                nozzl = 'nozzle_' + str(int(nozzl.split('_')[-1])-1)
                if nozzl in sparse_infill:
                    sparse_infill[nozzl].extend(lines)
                else:
                    sparse_infill.update({nozzl: lines})
            if layer not in self.sparse_infill:
                self.sparse_infill[layer] = [sparse_infill]
            else:
                self.sparse_infill[layer].append(sparse_infill)

    def _slicer_gen_solid_mask(self, layer_num):
        top_cnt = self.conf['top_layers']
        bot_cnt = self.conf['bottom_layers']
        # Solid Mask
        top_masks = self.top_masks[layer_num: layer_num + top_cnt]
        perims = self.perimeter_paths[layer_num]
        bot_masks = self.bot_masks[max(0, layer_num - bot_cnt + 1): layer_num + 1]
        out_mask = []
        for mask in top_masks:
            out_mask = geom.union(out_mask, geom.close_paths(mask))
        for mask in bot_masks:
            out_mask = geom.union(out_mask, geom.close_paths(mask))
        solid_mask = geom.clip(out_mask, perims[0])
        bounds = geom.paths_bounds(perims[0])
        return bounds, solid_mask, perims

    def _slicer_gen_solid_infill(self, solid_mask, bounds, layer_num):
        solid_infill = []
        base_ang = 45 if layer_num % 2 == 0 else -45
        solid_mask = geom.offset(solid_mask, self.conf['infill_overlap'] - self.extrusion_width)
        lines = geom.make_infill_lines(bounds, base_ang, 1.0, self.extrusion_width)
        for line in lines:
            lines = [line]
            lines = geom.clip(lines, solid_mask, subj_closed=False)
            solid_infill.extend(lines)
        self.solid_infill.append(solid_infill)

    def _slicer_task_pathing(self):
        # self.__slicer_task_pathing_nozzl()
        for slice_num in range(len(self.perimeter_paths)):

            # Enable or disable perimter here
            if self.enable_perims is not None:
                if self.enable_perims.isChecked() is True:
                    self.__slicer_task_pathing_perim(slice_num)
            else:
                self.__slicer_task_pathing_perim(slice_num)

            # Solid infill for bottom layers
            self.__slicer_task_pathing_bottom(slice_num)
            self.__slicer_task_pathing_infill(slice_num)

    def __slicer_task_pathing_infill(self, slice_num):
        layer = slice_num
        sparse_infills = self.sparse_infill[layer]
        for infill in sparse_infills:
            for nozl, sparse_infill in infill.items():
                infl_nozl = int(nozl.split('_')[-1])
                self._add_raw_layer_paths(layer, sparse_infill, self.infill_width, infl_nozl, [],
                                  'infill')

    def __slicer_task_pathing_bottom(self, slice_num):
        layer = slice_num
        self._add_raw_layer_paths(layer, self.solid_infill[slice_num], self.extrusion_width, self.dflt_nozl, [],
                                  'infill')

    def __slicer_task_pathing_perim(self, slice_num):
        for paths in self.perimeter_paths[slice_num]:
            layer = slice_num
            paths = geom.close_paths(paths)
            self._add_raw_layer_paths(layer, paths, self.extrusion_width, self.dflt_nozl, [], 'perimeter')

    def __slicer_task_pathing_nozzl(self):
        prime_nozls = [self.conf['default_nozzle']];
        if self.conf['infill_nozzle'] != -1:
            prime_nozls.append(self.conf['infill_nozzle']);
        if self.conf['support_nozzle'] != -1:
            prime_nozls.append(self.conf['support_nozzle']);
        center_x = self.conf['bed_center_x']
        center_y = self.conf['bed_center_y']
        size_x = self.conf['bed_size_x']
        size_y = self.conf['bed_size_y']
        minx = center_x - size_x / 2
        maxx = center_x + size_x / 2
        miny = center_y - size_y / 2
        maxy = center_y + size_y / 2
        bed_geom = self.conf['bed_geometry']
        rect_bed = bed_geom == 'Rectangular'
        cyl_bed = bed_geom == 'Cylindrical'
        maxlen = (maxy - miny - 20) if rect_bed else (2 * math.pi * math.sqrt((size_x * size_x) / 2) - 20)
        reps = self.conf['prime_length'] / maxlen
        ireps = int(math.ceil(reps))
        for noznum, nozl in enumerate(prime_nozls):
            ewidth = self.extrusion_width * 1.25
            nozl_path = []
            for rep in range(ireps):
                if rect_bed:
                    x = minx + 5 + (noznum * reps + rep + 1) * ewidth
                    if rep % 2 == 0:
                        y1 = miny + 10
                        y2 = maxy - 10
                    else:
                        y1 = maxy - 10
                        y2 = miny + 10
                    nozl_path.append([x, y1])
                    if rep == ireps - 1:
                        part = reps - math.floor(reps)
                        nozl_path.append([x, y1 + (y2 - y1) * part])
                    else:
                        nozl_path.append([x, y2])
                elif cyl_bed:
                    r = maxx - 5 - (noznum * reps + rep + 1) * ewidth
                    if rep == ireps - 1:
                        part = float(reps) - math.floor(reps)
                    else:
                        part = 1.0
                    steps = math.floor(2.0 * math.pi * r * part / 4.0)
                    stepang = 2 * math.pi / steps
                    for i in range(int(steps)):
                        nozl_path.append([r * math.cos(i * stepang), r * math.sin(i * stepang)])
            self._add_raw_layer_paths(0, [nozl_path], ewidth, noznum)

    def write_gcode_to_file(self, gcode_data, filename):
        # gcode_data = self._slicer_task_gcode()
        with open(filename, 'w') as f:
            f.write('\n'.join(gcode_data))

    def _slicer_task_gcode(self):
        total_layers = self.layers
        gcode_lines = []

        gcode_lines.append(";FLAVOR:Marlin")
        gcode_lines.append(";Layer height: {:.2f}".format(self.conf['layer_height']))

        if self.conf['gcode_comments']:
            gcode_lines.append(";generated by {:s} {:s} at {} from \"{:s}\"".format(self.NAME, self.VERSION,
                                                                                    datetime.datetime.now(),
                                                                                    ""))
        for k, v in sorted(self.conf.items()):
            if type(v) == str:
                v = v.replace("\n", '\\n')
            gcode_lines.append(";  {:s} = {}".format(k, v))

        gcode_lines.extend(["M82 ;absolute extrusion mode",
                            "G21 ;metric values",
                            "G90 ;absolute positioning",
                            "M107 ;Fan off"])

        if self.conf['bed_temp'] > 0:
            gcode_lines.extend(["M140 S{:d} ;set bed temp".format(self.conf['bed_temp']),
                                "M190 S{:d} ;wait for bed temp".format(self.conf['bed_temp'])])

        gcode_lines.append("M104 S{:d} ;set extruder0 temp".format(self.conf['nozzle_0_temp']))

        start_gcode = ";start gcode\n" + self.conf['start_gcode'].replace(r'\n', "\n") + "\n;/start gcode"
        gcode_lines.append(start_gcode)

        gcode_lines.extend(["M109 S{:d} ;wait for extruder0 temp".format(self.conf['nozzle_0_temp']),
                            "G92 E0 ;Zero extruder",
                            "M117 Printing...",
                            ";LAYER_COUNT:{}".format(total_layers)])

        for layer in range(total_layers):
            if self.conf['gcode_comments']:
                gcode_lines.append(";LAYER:{}".format(layer))

            if layer == self.conf['cool_fan_full_layer'] and self.conf['cool_fan_speed_max'] > 0:
                gcode_lines.append(
                    "M106 S{:d} ;cool_fan_full_layer".format(int(self.conf['cool_fan_speed_max'] * 255 / 100)))

            if layer in self.raw_layer_paths:
                layer_paths = self.raw_layer_paths[layer]
                for nozl, paths_data in layer_paths.items():
                    if not paths_data:
                        continue
                    gcode_lines.append(";( Nozzle {} )".format(nozl))
                    for paths, width, typ in paths_data:
                        for line in self._paths_gcode(paths, width, nozl, layer, self.layer_zs[layer], typ):
                            gcode_lines.append(line)

        end_gcode = ";end gcode\n" + self.conf['end_gcode'].replace(r'\n', "\n") + "\n;/end gcode"
        gcode_lines.append(end_gcode)

        return gcode_lines

    ###################################################################################################################
    def _vdist(self, a, b):
        delta = [x - y for x, y in zip(a, b)]
        dist = math.sqrt(sum([float(x) * float(x) for x in delta]))
        return dist

    def _add_raw_layer_paths(self, layer, paths, width, nozl, do_not_cross=[], typ=''):
        maxdist = 2.0
        joined = []
        if paths:
            path = paths.pop(0)
            while paths:
                mindist = 1e9
                minidx = None
                enda = False
                endb = False
                dists = [
                    [i, self._vdist(path[a], paths[i][b]), a == -1, b == -1]
                    for a in [0, -1]
                    for b in [0, -1]
                    for i in range(len(paths))
                ]
                for i, dist, ea, eb in dists:
                    if dist < mindist:
                        minidx, mindist, enda, endb = (i, dist, ea, eb)
                if mindist <= maxdist:
                    path2 = paths.pop(minidx)
                    if enda:
                        path = path + (list(reversed(path2)) if endb else path2)
                    else:
                        path = (path2 if endb else list(reversed(path2))) + path
                else:
                    if minidx is not None:
                        if enda == endb:
                            paths.insert(0, list(reversed(paths.pop(minidx))))
                        else:
                            paths.insert(0, paths.pop(minidx))
                    joined.append(path)
                    path = paths.pop(0)
            joined.append(path)

        if layer not in self.raw_layer_paths:
            self.raw_layer_paths[layer] = {}
        if nozl not in self.raw_layer_paths[layer]:
            self.raw_layer_paths[layer].update({nozl: []})

        self.raw_layer_paths[layer][nozl].append((joined, width, typ))

    def _tool_change_gcode(self, newnozl):
        retract_ext_dist = self.conf['retract_extruder']
        retract_speed = self.conf['retract_speed']
        if self.last_nozl == newnozl:
            return []
        gcode_lines = []
        gcode_lines.append(";tool change");
        gcode_lines.append("G1 E{e:.3f} F{f:g}".format(e=-retract_ext_dist, f=retract_speed * 60.0))
        gcode_lines.append("T{t:d}".format(t=newnozl))
        gcode_lines.append("G1 E{e:.3f} F{f:g}".format(e=retract_ext_dist, f=retract_speed * 60.0))
        gcode_lines.append(";/tool change");
        return gcode_lines

    def _paths_gcode(self, paths, ewidth, nozl, layer, z, typ='', last=0):
        if len(paths) <= 0:
            return []

        # -- copy some configs into local vars
        fil_diam = self.conf['nozzle_{0:d}_filament'.format(nozl)]
        nozl_diam = self.conf['nozzle_{0:d}_diam'.format(nozl)]
        max_speed = self.conf['nozzle_{0:d}_max_speed'.format(nozl)]
        feed_rate = self.conf['nozzle_{0:d}_feed_rate'.format(nozl)]
        extrusion_ratio = self.conf['nozzle_{0:d}_flow_rate'.format(nozl)]
        layer_height = self.conf['layer_height']
        retract_dist = self.conf['retract_dist']
        retract_speed = self.conf['retract_speed']
        retract_lift = self.conf['retract_lift']
        #feed_rate = self.conf['feed_rate']
        travel_rate_xy = self.conf['travel_rate_xy']
        travel_rate_z = self.conf['travel_rate_z']
        # print("------")
        # print(nozl)
        # print(feed_rate)

        # -- calculating some extrusion factor
        ewidth = nozl_diam * extrusion_ratio  # -- e.g. 0.4 * 1.25 = 0.5
        min_edist = nozl_diam / 2  # -- minimal edist based on nozl_diam
        speedf = 1

        if layer == 0:  # -- make thick first layer and slower
            ewidth *= 1.25
            speedf = 0.5
        elif typ == 'perimeter' and self.conf['shell_speed'] > 0:  # -- perimeters may have their own speed
            speedf = self.conf['shell_speed'] / max_speed
            if typ == 'perimeter' and last:  # -- FIXME: check for last (outer) perimeter/shell
                speedf = self.conf['external_shell_speed'] / max_speed
                # if self.args.debug:
                #     print("outer perimeter", z, layer, speedf, n, lnp)

        xsect = math.pi * ewidth / 2 * layer_height / 2  # -- e.g. pi * 0.5/2 * 0.2/2 = 0.0785 = oval cross section
        fil_xsect = math.pi * fil_diam / 2 * fil_diam / 2  # -- e.g. pi * 1.75/2 * 1.75/2 = 2.404 = filament cross section
        xsectf = xsect / fil_xsect

        gcode_lines = []

        # if self.conf['extruder_count'] > 1:  # -- only add if there are multiple extruders
        for line in self._tool_change_gcode(nozl):
            gcode_lines.append(line)

        if len(paths) > 0 and self.conf['gcode_comments']:
            gcode_lines.append(";SPEED:{:.0f}%".format(speedf * 100))
            gcode_lines.append(";TYPE:" + typ.upper() + "");

        if 0:
            # -- retract
            if len(paths) > 0 and (self.last_typ == 'infill' or self.last_typ == 'perimeter') and self.last_typ != typ:
                if typ != 'infill' and typ != 'perimeter':
                    self.total_build_time += abs(retract_dist) / retract_speed
                    self.last_e -= retract_dist
                    gcode_lines.append(
                        "G1 E{e:.3f} F{f:g} ;retract {t:s} ({lt:s})".format(e=self.last_e, f=retract_speed * 60.0,
                                                                              t=typ, lt=self.last_typ))
                    self.last_retract_typ = typ

            # -- unretract
            # if len(paths) > 0 and (self.last_typ == 'infill' or self.last_typ == 'perimeter') and self.last_typ != typ and self.last_typ != "":
            #    if typ == 'infill' or typ != 'perimeter':
            if len(paths) > 0 and (
                    self.last_typ == 'infill' or self.last_typ == 'perimeter') and self.last_typ != typ and self.last_typ != "":
                if self.last_retract_typ == 'infill' or self.last_retract_typ != 'perimeter':
                    self.total_build_time += abs(retract_dist) / retract_speed
                    self.last_e += retract_dist
                    gcode_lines.append(
                        "G1 E{e:.3f} F{f:g} ;unretract {t:s} ({lt:s})".format(e=self.last_e, f=feed_rate * 60.0,
                                                                                t=typ, lt=self.last_retract_typ))

        # -- all paths of single Z layer (z)
        for path in paths:
            if not path:
                continue
            ox, oy = path[0][0:2]  # -- origin coord, z disregarded (comes as argument)

            if retract_lift > 0 or self.last_pos[2] != z:  # -- reposition Z required?
                self.total_build_time += abs(retract_lift) / travel_rate_z
                gcode_lines.append("G1 Z{z:.2f} F{f:g}".format(z=z + retract_lift, f=travel_rate_z * 60.0))

            dist = math.hypot(self.last_pos[1] - oy, self.last_pos[0] - ox)  # -- distance to move (from last pos)
            self.total_build_time += dist / travel_rate_xy

            # -- we move to the beginning of the path (no extrusion yet)
            gcode_lines.append("G0 X{x:.2f} Y{y:.2f} F{f:g}".format(x=ox, y=oy, f=travel_rate_xy * 60.0))
            #gcode_lines.append("G0 X{x:.2f} Y{y:.2f} F{f:g}".format(x=ox, y=oy, f=feed_rate * 60.0))

            if retract_lift > 0:
                self.total_build_time += abs(retract_lift) / travel_rate_z
                gcode_lines.append("G1 Z{z:.2f} F{f:g}".format(z=z, f=travel_rate_z * 60.0))

            if retract_dist > 0:  # and typ != 'infill' and typ != 'perimeter':
                self.total_build_time += abs(retract_dist) / retract_speed
                self.last_e += retract_dist
                gcode_lines.append(
                    "G1 E{e:.3f} F{f:g} ;unretract {t:s}".format(e=self.last_e, f=feed_rate * 60.0, t=typ))

            for x, y in path[1:]:  # -- now we process the rest of the path
                dist = math.hypot(y - oy, x - ox)

                if dist < min_edist:  # -- this is needed, some models are too detailed, or -M scale=s creates tiny deltas
                    continue

                fil_dist = dist * xsectf
                # if self.args.debug:
                #    print("dist",dist,"fil_dist",fil_dist,"last_e",self.last_e)

                speed = min(feed_rate, max_speed) * 60.0 * speedf

                self.total_build_time += dist / feed_rate
                self.last_e += fil_dist

                # gcode_lines.append("G1 X{x:.2f} Y{y:.2f} E{e:.3f} F{f:g}".format(x=x, y=y, e=self.last_e, f=speed))
                gcode_lines.append("G1 X{x:.2f} Y{y:.2f} E{e:.3f}".format(x=x, y=y, e=self.last_e))
                self.last_pos = (x, y, z)
                ox, oy = x, y

            if retract_dist > 0:  # and typ != 'infill' and typ != 'perimeter':
                self.total_build_time += abs(retract_dist) / retract_speed
                self.last_e -= retract_dist
                gcode_lines.append(
                    "G1 E{e:.3f} F{f:g} ;retract {t:s}".format(e=self.last_e, f=retract_speed * 60.0, t=typ))

        if len(paths) > 0:
            self.last_typ = typ

        return gcode_lines

    ## ============================================== DRAW GCODE ============================================

    # def _redraw_paths(self, incdec=0):
    #     self.layer = min(max(0, self.layer + incdec), len(self.perimeter_paths) - 1 + self.raft_layers)
    #     layernum = self.layer
    #     layers = self.raft_layers + self.layers
    #     center_x = self.conf['bed_center_x']
    #     center_y = self.conf['bed_center_y']
    #     size_x = self.conf['bed_size_x']
    #     size_y = self.conf['bed_size_y']
    #     minx = (center_x - size_x / 2) * self.mag
    #     maxx = (center_x + size_x / 2) * self.mag
    #     miny = (center_y - size_y / 2) * self.mag
    #     maxy = (center_y + size_y / 2) * self.mag
    #
    #     # self.progbar['value'] = layernum
    #     # self.progbar['maximum'] = layers - 1
    #
    #     grid_colors = ["#ccf", "#eef"]
    #     for x in range(int(size_x / 10)):
    #         for y in range(int(size_y / 10)):
    #             rect = [val * 10 * self.mag for val in (x, y, x + 1, y + 1)]
    #             self.canvas.create_rectangle(rect, fill=grid_colors[(x + y) % 2])
    #     nozl_colors = [["#0c0"], ["#aa0"], ["#00c"], ["#c00"]]
    #     if layernum in self.raw_layer_paths:
    #         layer_paths = self.raw_layer_paths[layernum]
    #         for nozl, paths_data in layer_paths.items():
    #             if not paths_data:
    #                 continue
    #             for paths, width, typ in paths_data:
    #                 self._draw_line(paths, colors=nozl_colors[nozl], ewidth=width)
    #
    #     self._draw_line(self.layer_paths[self.layer], colors=["#cc0"], ewidth=self.extrusion_width / 8.0)
    #     self._draw_line(self.dead_paths[self.layer], colors=["red"], ewidth=self.extrusion_width / 8.0)

    def draw_line(self, paths, offset=0, colors=[Qt.red, Qt.green, Qt.blue], ewidth=0.5):
        center_x = self.conf['bed_center_x']
        center_y = self.conf['bed_center_y']
        size_x = self.conf['bed_size_x']
        size_y = self.conf['bed_size_y']
        minx = (center_x - size_x / 2) * self.mag
        maxx = (center_x + size_x / 2) * self.mag
        miny = (center_y - size_y / 2) * self.mag
        maxy = (center_y + size_y / 2) * self.mag

        for pathnum, path in enumerate(paths):
            path = [(x * self.mag, maxy - y * self.mag) for x, y in path]
            color = colors[(pathnum + offset) % len(colors)]
            # Create a QPen to style the lines
            pen = QPen(color, 2)
            pen.setJoinStyle(Qt.RoundJoin)
            pen.setWidthF(self.mag* ewidth)
            pen.setCapStyle(Qt.RoundCap)
            # for pa in path:
            #     for i in range(len(pa) - 1):
            #         x1, y1 = pa[i]
            #         x2, y2 = pa[i + 1]
            #         self.scene.addLine(QLineF(x1, y1, x2, y2), pen)