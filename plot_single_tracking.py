import json
import math
import glob

import ROOT
from xboa.hit import Hit
import xboa.common as common
import Configuration
import maus_cpp.field as field
import maus_cpp.globals as maus_globals

def load_json(file_name):
    print "Loading", file_name
    fin = open(file_name)
    data = [json.loads(line) for line in fin.readlines()]
    for item in data:
        item["seed"] = [Hit.new_from_dict(a_dict) for a_dict in item["seed"]]
    print "Loaded"
    return data

def filter_data(data, filter_lambdas):
    new_data = []
    for item in data:
        will_keep = True
        for a_lambda in filter_lambdas:
            if not a_lambda(item):
                will_keep = False
        if will_keep:
            new_data.append(item)
    return new_data

def plot_data_vs_delta(data, title, filter_lambdas, x_axis_lambda, x_axis_name, canvas_square = None, canvas_tri = None, line_color=1):
    data = filter_data(data, filter_lambdas)

    if len(data) == 0:
        return canvas_square, canvas_tri
    print "plot", title
    delta_list = [x_axis_lambda(item) for item in data]
    triangle_list = [abs(item["an_area_list"][-1]/item["an_area_list"][0]-1) for item in data]
    square_list = [abs(sum(item["area_list_of_lists"][-1])/sum(item["area_list_of_lists"][0])-1) for item in data]
    print triangle_list, delta_list
    ymin=min(square_list+triangle_list)*0.1
    ymax=max(square_list+triangle_list)*1.1


    hist, graph = common.make_root_graph("step size "+str(data[0]['step_size'])+" mm",
                              delta_list, x_axis_name,
                              triangle_list, "Fractional change in simplex content",
                              xmin=min(delta_list)*0.9, ymin=ymin, ymax=ymax)
    if canvas_tri == None:
        canvas_tri = common.make_root_canvas("delta triangles - "+title)
        canvas_tri.SetLogy()
        hist.Draw()
    hist.SetTitle(title)
    canvas_tri.cd()
    graph.SetLineColor(line_color)
    graph.SetMarkerStyle(24)
    graph.Draw("SAMEPL")
    canvas_tri.Update()
    hist, graph = common.make_root_graph("step size "+str(data[0]['step_size'])+" mm",
                                         delta_list, x_axis_name,
                                         square_list, "Fractional change in hypercube content",
                                         xmin=min(delta_list)*0.9, ymin=ymin, ymax=ymax)
    hist.SetTitle(title)
    if canvas_square == None:
        canvas_square = common.make_root_canvas("delta triangles - "+title)
        canvas_square.SetLogy()
        hist.Draw()
    canvas_square.cd()
    graph.SetLineColor(line_color)
    graph.SetMarkerStyle(24)
    graph.Draw("SAMEPL")
    canvas_square.Update()

    return canvas_square, canvas_tri
    
def plot_x_px():
    data = load_json("single_tracking_x-px.json")
    data = [item for item in data if None not in item["area_list_of_lists"][-1]]
    filter_lambdas = [
        lambda item: abs(item['seed'][0]['x']) < 1e-6
    ]
    x_axis_lambda = lambda item: item['seed'][0]['px']
    csq, ctri = plot_data_vs_delta(data, "px varying", filter_lambdas, x_axis_lambda, "initial px [MeV/c]")
    ctri.Print("plots/phase_space_volume_vs_initial_px.png")
    ctri.Print("plots/phase_space_volume_vs_initial_px.root")

    filter_lambdas = [
        lambda item: abs(item['seed'][0]['px']) < 1e-6
    ]
    x_axis_lambda = lambda item: item['seed'][0]['x']
    csq, ctri = plot_data_vs_delta(data, "x varying", filter_lambdas, x_axis_lambda, "initial x [mm]")
    ctri.Print("plots/phase_space_volume_vs_initial_x.png")
    ctri.Print("plots/phase_space_volume_vs_initial_x.root")

def plot_z(item, line_color, do_square, canvas = None):
    z_list = [hit["z"] for hit in item["seed"]]
    if not do_square: #i.e. do triangle
        area_list = [abs(area/item["an_area_list"][0]-1) for area in item["an_area_list"]]
    else:
        area_list = [abs(sum(area_list)/sum(item["area_list_of_lists"][0])-1) for area_list in item["area_list_of_lists"]]

    title = "x: "+str(item["seed"][0]["x"])+" mm "+\
            "p_{x}: "+str(item["seed"][0]["px"])+" MeV/c"
    hist, graph = common.make_root_graph(title,
                              z_list, "z [mm]",
                              area_list, "Fractional change in simplex content",
                              ymin = 1e-5, ymax=100.
                  )
    if canvas == None:
        canvas = common.make_root_canvas("content growth vs z")
        canvas.SetLogy()
        hist.Draw()
    canvas.cd()
    graph.SetLineColor(line_color)
    graph.Draw("SAMEPL")
    canvas.Update()
    return canvas, graph
    
def plot_trajectory(item, line_color, canvas = None):
    z_list = [hit["z"] for hit in item["seed"]]
    x_list = [hit["x"] for hit in item["seed"]]
    y_list = [hit["y"] for hit in item["seed"]]
    r_list = [hit["r"] for hit in item["seed"]]

    x_min, x_max = common.min_max(x_list+r_list+y_list)
    title = "x: "+str(item["seed"][0]["x"])+" mm "+\
            "p_{x}: "+str(item["seed"][0]["px"])+" MeV/c"
    hist_r, graph_r = common.make_root_graph(title, z_list, "z [mm]", r_list, "Radius [mm]", ymin=0.0, ymax=250.)
    hist_x, graph_x = common.make_root_graph("x", z_list, "z [mm]", x_list, "Position [mm]")
    hist_y, graph_y = common.make_root_graph("y", z_list, "z [mm]", y_list, "Position [mm]")
    graph_r.SetLineColor(line_color)
    graph_x.SetLineColor(line_color)
    graph_x.SetLineStyle(3)
    graph_y.SetLineColor(line_color)
    graph_y.SetLineStyle(4)
    if canvas == None:
        canvas = common.make_root_canvas("trajectory")
        #hist_r.SetTitle("x = "+str(x_list[0])+" px = "+str(item["seed"][0]["px"]))
        hist_r.Draw()
    canvas.cd()
    graph_r.Draw("SAMEPL")
    #graph_x.Draw("SAMEPL")
    #graph_y.Draw("SAMEPL")
    canvas.Update()

    return canvas, graph_r


def plot_delta():
    for x, px in [(0., 10.), (0., 0.), (100., 0.), ]:
        csq, ctri = None, None
        for i, filename in enumerate(glob.glob("single_tracking_short_coil.json")):
            data = load_json(filename)
            line_color = [2, 4, 6, 8]
            data = [item for item in data if None not in item["area_list_of_lists"][-1]]
            filter_lambdas = [
                lambda item: abs(item['seed'][0]['x']-x) < 1e-6,
                lambda item: abs(item['seed'][0]['px']-px) < 1e-6
            ]
            x_axis_lambda = lambda item: item['delta']['x']
            csq, ctri = plot_data_vs_delta(data, "x="+str(x)+" mm px="+str(px)+" MeV/c", filter_lambdas, x_axis_lambda, "delta [mm or MeV/c]", csq, ctri, line_color[i])
            if csq != None:
                csq.SetLogx()
                ctri.SetLogx()
            csq.Print("plots/simplex_phase_space_volume_vs_delta_x="+str(x)+"_px="+str(px)+".png")
            csq.Print("plots/simplex_phase_space_volume_vs_delta_x="+str(x)+"_px="+str(px)+".root")
            ctri.Print("plots/hypercube_phase_space_volume_vs_delta_x="+str(x)+"_px="+str(px)+".png")
            ctri.Print("plots/hypercube_phase_space_volume_vs_delta_x="+str(x)+"_px="+str(px)+".root")

def get_axis(x_list):
    x_axis = sorted([x for x in set(x_list)])
    n_x_bins = len(x_axis)
    x_step = (max(x_axis)-min(x_axis))/(n_x_bins-1)
    x_min = min(x_axis)-x_step
    x_max = max(x_axis)-x_step
    return x_min, x_max, n_x_bins

bfield_hist = None
bfield_graph = None
def get_b_field(canvas, z = None):
    global bfield_hist, bfield_graph
    if not maus_globals.has_instance():
        configuration = Configuration.Configuration().\
                                          getConfigJSON(command_line_args=True)

        maus_globals.birth(configuration)
        z_list = []
        bz_list = []
        for z_pos in range(-8000, 8001, 50):
            z_pos = float(z_pos)
            (bx_field, by_field, bz_field, ex_field, ey_field, ez_field) = \
                                            field.get_field_value(0., 0., z_pos, 0.)
            z_list.append(z_pos)  # z in mm
            bz_list.append(bz_field*1e3)  # bz in T
        bfield_hist, bfield_graph = common.make_root_graph("bz vs z", z_list, "z [m]",
                                                             bz_list, "B_{z} [T]")
    canvas.cd()
    bfield_hist.Draw()
    bfield_graph.Draw('l')
    if z != None:
        print "Plotting z", z
        marker_graph = ROOT.TGraph(2)
        marker_graph.SetPoint(0, z, -1000)
        marker_graph.SetPoint(1, z, +1000)
        marker_graph.Draw('l')
        root_list.append(marker_graph)

root_list = []
def plot_heat(data, plane = None, canvas = None):
    if plane != None:
        print "Doing plane", plane
    data = filter_data(data, [lambda item: item["an_area_list"][-1] != None],)
    data = filter_data(data, [lambda item: item["seed"][-1]["r"] < 1e3],)
 
    triangle_list = []
    for item in data:
        if plane == None:
            triangle_list.append(abs(item["an_area_list"][-1]/item["an_area_list"][0]-1))
        else:
            if plane < len(item["an_area_list"]):
                triangle_list.append(abs(item["an_area_list"][plane]/item["an_area_list"][0]-1))
            else:
                triangle_list.append(1e9)
    x_list = [item["seed"][0]["x"] for item in data]
    px_list = [item["seed"][0]["px"] for item in data]
    
    x_min, x_max, n_x_bins = get_axis(x_list)
    px_min, px_max, n_px_bins = get_axis(px_list)
    if canvas == None:
        canvas = common.make_root_canvas("heating map")
        if plane != None:
            canvas.SetCanvasSize(700, 1000)
            canvas.Divide(1, 2)
    if plane != None:       
        canvas.cd(2)
        get_b_field(canvas.GetPad(2), z = item["seed"][plane]["z"])
        canvas.cd(1)
        canvas.GetPad(1).SetLogz()
    hist = ROOT.TH2D("heating map", ";x [mm];p_{x} [MeV/c]", n_x_bins, x_min, x_max, n_px_bins, px_min, px_max)
    hist.SetStats(False)
    z_min, z_max = 1e-4, 100.
    hist.GetZaxis().SetRangeUser(z_min, z_max)
    canvas.Draw()
    for i, content in enumerate(triangle_list):
        bin = hist.FindBin(x_list[i], px_list[i])
        if content < z_min:
            content = z_min*1.00001
        if content > z_max:
            content = z_max*0.99999
        hist.SetBinContent(bin, content)
    hist.Draw("COLZ")
    root_list.append(hist)
    canvas.SetLogz()
    canvas.Update()
    if plane == None:
        canvas.Print("plots/heat_map.png")
    else:
        name = str(plane).rjust(4, '0')
        canvas.Print("plots/heat_map_"+name+".gif")
    return canvas

def select(data, x_px_list):
    selected_list = []
    for item in data:
        for x, px in x_px_list:
            if abs(item["seed"][0]["x"] - x) < 1e-3 and abs(item["seed"][0]["px"] - px) < 1e-3:
                selected_list.append(item)
                break
    return selected_list

def main():
    data = load_json("single_tracking.json")
    plot_heat(data)
    heat_canvas = None
    for plane in range(len(data[0]["an_area_list"])):
        heat_canvas = plot_heat(data, plane, heat_canvas)

    graph_z_list = []
    graph_traj_list = []
    canvas_z = None
    canvas_traj = None
    line_color_index = 0
    plot_data = select(data, [(a*20., a*2.) for a in range(11)])
    for item in reversed(plot_data):
        line_color_index += 1
        pos = 1.*line_color_index/(len(plot_data)+1)
        red = 0.5*(math.sin(2*math.pi*pos)+1.)
        green = 0.5*(math.cos(2*math.pi*pos)+1.)
        blue = 0.5
        norm = (red**2+green**2+blue**2)**0.5
        red, green, blue = red/norm, green/norm, blue/norm
        line_color = ROOT.TColor.GetColor(red, green, blue)
        canvas_z, graph_z = plot_z(item, line_color, False, canvas_z)
        canvas_traj, graph_traj = plot_trajectory(item, line_color, canvas_traj)
        graph_z_list.append(graph_z)
        graph_traj_list.append(graph_traj)
    common.make_root_legend(canvas_traj, graph_traj_list)
    common.make_root_legend(canvas_z, graph_z_list)
    #canvas_z.Print("plots/content_vs_z.png")
    #canvas_traj.Print("plots/radius_vs_z.png")

if __name__ == "__main__":
    main()
    raw_input()

