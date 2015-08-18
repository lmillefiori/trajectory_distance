import matplotlib.pyplot as plt
import matplotlib.colors as colors
from utils.config import *
import Geohash.geohash as geoh
import shapely.geometry as geos
import matplotlib.patches as mpatches
from matplotlib.collections import PatchCollection
CMAP = plt.get_cmap('Paired')

def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=100):
    new_cmap = colors.LinearSegmentedColormap.from_list(
        'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=minval, b=maxval),
        cmap(np.linspace(minval, maxval, n)))
    return new_cmap

CMAP_HIST = truncate_colormap(plt.get_cmap("Blues"),0.2,1)


def lines_cell_lons_bigger(p1,p2,precision):
    reverse=False
    if p2[1]<p1[1]:
        tmp=p1
        p1=p2
        p2=tmp
        reverse=True

    if p1[0]<p2[0]:
        order="croissant"
        idx_step=1
    else:
        order="decroissant"
        idx_step=-1

    p1e=geoh.encode(p1[1],p1[0],precision)
    p2e=geoh.encode(p2[1],p2[0],precision)
    line = geos.LineString([p1,p2])
    lat1,lon1,dlat,dlon=geoh.decode_exactly(p1e)
    lat2,lon2,dlat,dlon=geoh.decode_exactly(p2e)


    lats=np.arange(lat1-dlat,lat2+3*dlat,dlat*2)
    lons=np.arange(lon1-idx_step*dlon,lon2+idx_step*(3*dlon),idx_step*dlon*2)
    lats_center=np.arange(lat1,lat2+2*dlat,dlat*2)
    lons_center=np.arange(lon1,lon2+idx_step*(2*dlon),idx_step*dlon*2)

    nlons=len(lons)-2

    if order=="croissant":
        cell = [[0,0]]
    else:
        cell = [[nlons,0]]
        lons_center = lons_center[::-1]

    lons_inter = []
    for l in lons[1:-1]:
        lons_shape=geos.LineString([[l,lats[0]],[l,lats[-1]]])
        lons_inter.append(lons_shape.intersection(line))

    idx_lat = 0
    for p_int in lons_inter:
        if p_int.y<lats[idx_lat+1]:
            cell.append([cell[-1][0]+idx_step,cell[-1][1]])
        else:
            cell.append([cell[-1][0],cell[-1][1]+1])
            cell.append([cell[-1][0]+idx_step,cell[-1][1]])
            idx_lat+=1
    if lat2>lats[idx_lat+1]:
        cell.append([cell[-1][0],cell[-1][1]+1])
    #if lat2 > lats[-2]:
    #    cell.append([cell[-1][0],cell[-1][1]+1])
    if reverse:
        cell.reverse()
    cells_coord = map(lambda x : [lons_center[x[0]],lats_center[x[1]]], cell)
    return cells_coord,cell,lons,lats


def lines_cell_lats_bigger(p1,p2,precision):
    reverse=False
    if p2[0]<p1[0]:
        tmp=p1
        p1=p2
        p2=tmp
        reverse=True

    if p1[1]<p2[1]:
        order="croissant"
        idx_step=1
    else:
        order="decroissant"
        idx_step=-1

    p1e=geoh.encode(p1[1],p1[0],precision)
    p2e=geoh.encode(p2[1],p2[0],precision)
    line = geos.LineString([p1,p2])
    lat1,lon1,dlat,dlon=geoh.decode_exactly(p1e)
    lat2,lon2,dlat,dlon=geoh.decode_exactly(p2e)


    lats=np.arange(lat1-idx_step*dlat,lat2+idx_step*(3*dlat),idx_step*dlat*2)
    lons=np.arange(lon1-dlon,lon2+3*dlon,dlon*2)

    lats_center=np.arange(lat1,lat2+idx_step*(2*dlat),idx_step*dlat*2)
    lons_center=np.arange(lon1,lon2+2*dlon,dlon*2)

    nlats=len(lats)-2

    if order=="croissant":
        cell = [[0,0]]
    else:
        cell = [[0,nlats]]
        lats_center=lats_center[::-1]

    lats_inter = []
    for l in lats[1:-1] :
        lats_shape=geos.LineString([[lons[0],l],[lons[-1],l]])
        lats_inter.append(lats_shape.intersection(line))

    idx_lon = 0
    for p_int in lats_inter:
        if p_int.x<lons[idx_lon+1]:
            cell.append([cell[-1][0],cell[-1][1]+idx_step])
        else:
            cell.append([cell[-1][0]+1,cell[-1][1]])
            cell.append([cell[-1][0],cell[-1][1]+idx_step])
            idx_lon+=1
    if lon2>lons[idx_lon+1]:
        cell.append([cell[-1][0]+1,cell[-1][1]])
    if reverse:
        cell.reverse()
    cells_coord = map(lambda x : [lons_center[x[0]],lats_center[x[1]]], cell)
    return cells_coord,cell,lons,lats


def plot_line_cells_segment(fig,ax,p1,p2,lons,lats,cells,cells_coord):

    maplon = [min(lons),max(lons)]
    maplat = [min(lats),max(lats)]

    lons=sorted(lons)
    lats=sorted(lats)
    m = Basemap(maplon[0],maplat[0],maplon[1],maplat[1],ax=ax)
    #latitude
    for l in lats :
        m.plot([maplon[0],maplon[1]],[l,l],linestyle="-",color="black")
    #longitude
    for l in lons :
        m.plot([l,l],[maplat[0],maplat[1]],linestyle="-",color="black")
    for idx,(x,y) in enumerate(cells_coord):
        plt.text(x,y,"%d \n (%.3f,%.3f)"%(idx,cells_coord[idx][0],cells_coord[idx][1]),
                 verticalalignment="center",horizontalalignment="center",fontsize=6)
    #plot segment exemple
    x,y = m([p1[0],p2[0]],[p1[1],p2[1]])
    plt.text(p1[0],p1[1],r"$p_{1}$",color="grey")
    plt.text(p2[0],p2[1],r"$p_{2}$",color="grey")
    m.plot(x,y,marker=".", linestyle="-",color="grey")

    ax.set_xlim(maplon[0],maplon[1])
    ax.set_ylim(maplat[0],maplat[1])


def linecell_lons_bigger_step(p1,p2,cell_start,lons_all,lats_all,lons_center_all,lats_center_all):

    reverse=False
    if p2[1]<p1[1]:
        tmp=p1
        p1=p2
        p2=tmp
        reverse=True

    lats_start_index = np.where(lats_all<p1[1])[0][-1]
    lats_end_index = np.where(lats_all>p2[1])[0][0]
    lats = lats_all[lats_start_index:lats_end_index+1]



    if p1[0]<p2[0]:
        order="croissant"
        idx_step=1
        lons_start_index = np.where(lons_all<p1[0])[0][-1]
        lons_end_index = np.where(lons_all>p2[0])[0][0]
        lons = lons_all[lons_start_index:lons_end_index+1]
    else:
        order="decroissant"
        idx_step=-1
        lons_start_index = np.where(lons_all<p2[0])[0][-1]
        lons_end_index = np.where(lons_all>p1[0])[0][0]
        lons = lons_all[lons_start_index:lons_end_index+1]
        lons = lons[::-1]
    line = geos.LineString([p1,p2])

    nlons=len(lons)-2
    nlats=len(lats)-2


    if not(reverse):
        cell = [cell_start]
    else:
        if order=="croissant":
            cell = [[cell_start[0]-nlons,cell_start[1]-nlats]]
        else:
            cell = [[cell_start[0]+nlons,cell_start[1]-nlats]]

    lons_inter = []
    for l in lons[1:-1]:
        lons_shape=geos.LineString([[l,lats[0]],[l,lats[-1]]])
        lons_inter.append(lons_shape.intersection(line))

    idx_lat = 0
    for p_int in lons_inter:
        if p_int.y<lats[idx_lat+1]:
            cell.append([cell[-1][0]+idx_step,cell[-1][1]])
        else:
            cell.append([cell[-1][0],cell[-1][1]+1])
            cell.append([cell[-1][0]+idx_step,cell[-1][1]])
            idx_lat+=1
    if p2[1]>lats[idx_lat+1]:
        cell.append([cell[-1][0],cell[-1][1]+1])
    if reverse:
        cell.reverse()
    cells_coord = map(lambda x : [lons_center_all[x[0]],lats_center_all[x[1]]], cell)
    return cell,cells_coord

def linecell_lats_bigger_step(p1,p2,cell_start,lons_all,lats_all,lons_center_all,lats_center_all):

    reverse=False
    if p2[0]<p1[0]:
        tmp=p1
        p1=p2
        p2=tmp
        reverse=True

    lons_start_index = np.where(lons_all<p1[0])[0][-1]
    lons_end_index = np.where(lons_all>p2[0])[0][0]
    lons = lons_all[lons_start_index:lons_end_index+1]

    if p1[1]<p2[1]:
        order="croissant"
        idx_step=1
        lats_start_index = np.where(lats_all<p1[1])[0][-1]
        lats_end_index = np.where(lats_all>p2[1])[0][0]
        lats = lats_all[lats_start_index:lats_end_index+1]
    else:
        order="decroissant"
        idx_step=-1
        lats_start_index = np.where(lats_all<p2[1])[0][-1]
        lats_end_index = np.where(lats_all>p1[1])[0][0]
        lats = lats_all[lats_start_index:lats_end_index+1]
        lats = lats[::-1]
    line = geos.LineString([p1,p2])

    nlons=len(lons)-2
    nlats=len(lats)-2


    if not(reverse):
        cell = [cell_start]
    else:
        if order=="croissant":
            cell = [[cell_start[0]-nlons,cell_start[1]-nlats]]
        else:
            cell = [[cell_start[0]-nlons,cell_start[1]+nlats]]

    lats_inter = []
    for l in lats[1:-1]:
        lats_shape=geos.LineString([[lons[0],l],[lons[-1],l]])
        lats_inter.append(lats_shape.intersection(line))

    idx_lon = 0
    for p_int in lats_inter:
        if p_int.x<lons[idx_lon+1]:
            cell.append([cell[-1][0],cell[-1][1]+idx_step])
        else:
            cell.append([cell[-1][0]+1,cell[-1][1]])
            cell.append([cell[-1][0],cell[-1][1]+idx_step])
            idx_lon+=1
    if p2[0]>lons[idx_lon+1]:
        cell.append([cell[-1][0]+1,cell[-1][1]])
    if reverse:
        cell.reverse()
    cells_coord = map(lambda x : [lons_center_all[x[0]],lats_center_all[x[1]]], cell)
    return cell,cells_coord

def get_extremum(traj):
    lons=traj[:,0]
    lats=traj[:,1]
    min_lon=min(lons)
    min_lat=min(lats)
    max_lon=max(lons)
    max_lat=max(lats)
    return min_lon,min_lat,max_lon,max_lat



def trajectory_set_grid(traj_set,precision):
    extremums=np.array(map(get_extremum,traj_set))
    p_bottom_left=[min(extremums[:,0]),min(extremums[:,1])]
    p_top_right=[max(extremums[:,2]),max(extremums[:,3])]
    p_ble=geoh.encode(p_bottom_left[1],p_bottom_left[0],precision)
    p_tre=geoh.encode(p_top_right[1],p_top_right[0],precision)
    lat_ble,lon_ble,dlat,dlon=geoh.decode_exactly(p_ble)
    lat_tre,lon_tre,dlat,dlon=geoh.decode_exactly(p_tre)
    lats_all=np.arange(lat_ble-dlat,lat_tre+(3*dlat),dlat*2)
    lons_all=np.arange(lon_ble-dlon,lon_tre+3*dlon,dlon*2)
    lats_center_all=np.arange(lat_ble,lat_tre+2*dlat,dlat*2)
    lons_center_all=np.arange(lon_ble,lon_tre+2*dlon,dlon*2)

    cells_traj=[]
    for traj in traj_set:
        p_start = traj[0]
        cell_start_x = np.where(lons_all<p_start[0])[0][-1]
        cell_start_y = np.where(lats_all<p_start[1])[0][-1]
        cell_start = [cell_start_x,cell_start_y]

        cells = []

        for id_seg in range(len(traj)-1):

            start=traj[id_seg]
            end = traj[id_seg+1]
            if abs(start[0]-end[0])/dlon > abs(start[1]-end[1])/dlat:
                cell,cells_coord=linecell_lons_bigger_step(start,end,cell_start,lons_all,lats_all,lons_center_all,lats_center_all)
            else:
                cell,cells_coord=linecell_lats_bigger_step(start,end,cell_start,lons_all,lats_all,lons_center_all,
                                                          lats_center_all)
            cells.extend(cell[:-1])
            cell_start=cell[-1]
        cells.append(cell_start)
        cells_traj.append(cells)
    return cells_traj,lons_all,lats_all


def trajectory_grid(traj_0,precision):
    cells_list,lons_all,lats_all=trajectory_set_grid([traj_0],precision)
    return cells_list[0],lons_all,lats_all



def plot_line_cells_trajectory(fig,ax,traj,lons,lats,cells,display="number",grid=True,patch=False,plot_traj=True):

    maplon = [min(lons),max(lons)]
    maplat = [min(lats),max(lats)]
    dlon=(lons[1]-lons[0])/2
    dlat=(lats[1]-lats[0])/2
    lons_center=lons[:-1]+dlon
    lats_center=lats[:-1]+dlat

    #lons=sorted(lons)
    #lats=sorted(lats)


    m = Basemap(maplon[0],maplat[0],maplon[1],maplat[1],ax=ax)
    if grid:
        #latitude
        for l in lats :
            m.plot([maplon[0],maplon[1]],[l,l],linestyle="-",color="black")
        #longitude
        for l in lons :
            m.plot([l,l],[maplat[0],maplat[1]],linestyle="-",color="black")

    #plot segment exemple
    if plot_traj:
        x,y = m(traj[:,0],traj[:,1])
        m.plot(x,y,marker=".", linestyle="-",color="grey")
        plt.text(x[0],y[0],"start",fontsize=6,color="grey")
        plt.text(x[-1],y[-1],"end",fontsize=6,color="grey")

    #plot linecell
    if display=="order":
        for idx,(x,y) in enumerate(cells):
            plt.text(lons_center[x],lats_center[y],"%d" %(idx),fontsize=6,verticalalignment="center",
                     horizontalalignment="center",
                     color="blue")
    elif display=="cell":
        for idx,(x,y) in enumerate(cells):
            plt.text(lons_center[x],lats_center[y],"(%d,%d)" %(x,y),fontsize=5,verticalalignment="center",
                     horizontalalignment="center",
                     color="blue")
    elif display=="coord":
        for idx,(x,y) in enumerate(cells):
            plt.text(lons_center[x],lats_center[y],"(%.3f \n %.3f)" %(lons_center[x],lats_center[y]),fontsize=3,
                     verticalalignment="center",
                     horizontalalignment="center",
                     color="blue")
    if patch:
        patches=[]
        for idx,(x,y) in enumerate(cells):
            rect=mpatches.Rectangle([lons_center[x]-dlon,lats_center[y]-dlat],2*dlon,2*dlat,color="blue")
            patches.append(rect)
        collection = PatchCollection(patches)
        ax.add_collection(collection)


    ax.set_xlim(maplon[0],maplon[1])
    ax.set_ylim(maplat[0],maplat[1])

def plot_line_cells_trajectory_set(fig,ax,traj_list,lons,lats,cells_list,grid=True,patch="None",
                                   plot_traj=True,cmap=CMAP):

    maplon = [min(lons),max(lons)]
    maplat = [min(lats),max(lats)]
    dlon=(lons[1]-lons[0])/2
    dlat=(lats[1]-lats[0])/2
    lons_center=lons[:-1]+dlon
    lats_center=lats[:-1]+dlat
    nb_traj=len(traj_list)

    m = Basemap(maplon[0],maplat[0],maplon[1],maplat[1],ax=ax)
    if grid:
        #latitude
        for l in lats :
            m.plot([maplon[0],maplon[1]],[l,l],linestyle="-",color="black")
        #longitude
        for l in lons :
            m.plot([l,l],[maplat[0],maplat[1]],linestyle="-",color="black")

    #plot segment exemple
    if plot_traj:
        for i_traj,traj in enumerate(traj_list):
            x,y = m(traj[:,0],traj[:,1])
            color=cmap(int(i_traj * 225 / (nb_traj - 1)))
            m.plot(x,y,marker=".", linestyle="-",color=color)
            plt.text(x[0],y[0],"start",fontsize=6,color=color)
            plt.text(x[-1],y[-1],"end",fontsize=6,color=color)

    if patch=="simple":
        for i_traj,cells in enumerate(cells_list):
            for idx,(x,y) in enumerate(cells):
                rect=mpatches.Rectangle([lons_center[x]-dlon,lats_center[y]-dlat],2*dlon,2*dlat,facecolor=cmap(int(
                    i_traj * 225 / (nb_traj - 1))))
                ax.add_patch(rect)
    elif patch=="hist":
        all_cell=reduce(lambda x,y :x+y,cells_list)
        counter= collections.Counter(map(tuple,all_cell))
        max_c= max(counter.values())
        patches=[]
        my_colors=[]
        for i_traj,cells in enumerate(cells_list):
            for idx,(x,y) in enumerate(cells):
                color=counter[(x,y)]
                rect=mpatches.Rectangle([lons_center[x]-dlon,lats_center[y]-dlat],2*dlon,2*dlat)
                patches.append(rect)
                my_colors.append(color)
        rect_collection=PatchCollection(patches,cmap=CMAP_HIST)
        rect_collection.set_array(np.array(my_colors))
        ax.add_collection(rect_collection)
        fig.colorbar(rect_collection)

    ax.set_xlim(maplon[0],maplon[1])
    ax.set_ylim(maplat[0],maplat[1])
