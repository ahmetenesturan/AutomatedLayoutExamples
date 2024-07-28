from gdsfactory import Component
from glayout.flow.pdk.mappedpdk import MappedPDK
from glayout.flow.placement.two_transistor_interdigitized import two_nfet_interdigitized
from glayout.flow.placement.two_transistor_interdigitized import two_pfet_interdigitized
from glayout.flow.pdk.util.comp_utils import prec_ref_center, movey, evaluate_bbox
from glayout.flow.routing.smart_route import smart_route
from glayout.flow.routing.c_route import c_route

from glayout.flow.pdk.sky130_mapped import sky130_mapped_pdk

def DiffPair(pdk: MappedPDK, width, length):
    DiffPair = Component(name="DiffPair")
    diffp = two_nfet_interdigitized(pdk, numcols=2, dummy=True, with_substrate_tap=False, with_tie=True, width=width, length=length, rmult=1)
    diffp_ref = prec_ref_center(diffp)
    DiffPair.add(diffp_ref)
    DiffPair.add_ports(diffp_ref.get_ports_list(), prefix="diffp_")
    DiffPair << smart_route(pdk,DiffPair.ports["diffp_A_source_E"], DiffPair.ports["diffp_B_source_E"],diffp_ref,DiffPair)
    return DiffPair

def CurrentMirror(pdk: MappedPDK, width, length, type):
    CurrentMirror = Component(name="CurrentMirror")
    if type == "pfet":
        currm = two_pfet_interdigitized(pdk, numcols=2, dummy=True, with_substrate_tap=False, with_tie=True, width=width, length=length, rmult=1)
    elif type == "nfet":
        currm = two_nfet_interdigitized(pdk, numcols=2, dummy=True, with_substrate_tap=False, with_tie=True, width=width, length=length, rmult=1)
    currm_ref = prec_ref_center(currm)
    CurrentMirror.add(currm_ref)
    CurrentMirror.add_ports(currm_ref.get_ports_list(), prefix="currm_")
    CurrentMirror << smart_route(pdk,CurrentMirror.ports["currm_A_gate_E"], CurrentMirror.ports["currm_B_gate_E"],currm_ref,CurrentMirror)
    CurrentMirror << smart_route(pdk,CurrentMirror.ports["currm_A_drain_E"], CurrentMirror.ports["currm_A_gate_E"],currm_ref,CurrentMirror)
    CurrentMirror << smart_route(pdk,CurrentMirror.ports["currm_A_source_E"], CurrentMirror.ports["currm_B_source_E"],currm_ref,CurrentMirror)
    return CurrentMirror

def diffAmp(pdk: MappedPDK, cm_width, cm_length, diffp_width, diffp_length):
    diffAmp = Component(name="diffAmp")
    currMirr = CurrentMirror(pdk, cm_width, cm_length, "pfet")
    diffPair = DiffPair(pdk, diffp_width, diffp_length)
    sink = CurrentMirror(pdk, cm_width, cm_length, "nfet")
    currMirr_ref = prec_ref_center(currMirr)
    diffPair_ref = prec_ref_center(diffPair)
    sink_ref = prec_ref_center(sink)
    diffAmp.add(currMirr_ref)
    diffAmp.add(diffPair_ref)
    diffAmp.add(sink_ref)
    movey(currMirr_ref, evaluate_bbox(diffPair)[1]+pdk.util_max_metal_seperation())
    sink_offset = -(evaluate_bbox(diffPair)[1]+pdk.util_max_metal_seperation())
    movey(sink_ref, sink_offset)
    diffAmp << c_route(pdk, currMirr_ref.ports["currm_A_gate_W"], diffPair_ref.ports["diffp_A_drain_W"])
    diffAmp << c_route(pdk, currMirr_ref.ports["currm_B_drain_E"], diffPair_ref.ports["diffp_B_drain_E"])
    diffAmp << c_route(pdk, diffPair_ref.ports["diffp_A_source_E"], sink_ref.ports["currm_B_drain_E"])
    return diffAmp

diffAmp(sky130_mapped_pdk,2,2,2,2).show()