from gdsfactory import Component
from glayout.flow.pdk.mappedpdk import MappedPDK
from glayout.flow.placement.two_transistor_interdigitized import two_nfet_interdigitized
from glayout.flow.placement.two_transistor_interdigitized import two_pfet_interdigitized
from glayout.flow.pdk.util.comp_utils import prec_ref_center, movey, evaluate_bbox
from glayout.flow.routing.smart_route import smart_route
from glayout.flow.routing.c_route import c_route

from glayout.flow.pdk.sky130_mapped import sky130_mapped_pdk

from glayout.flow.primitives.fet import nmos
from glayout.flow.primitives.resistor import resistor
from glayout.flow.routing.straight_route import straight_route

from glayout.flow.blocks.opamp.opamp import opamp


def CommonSourceTran(pdk: MappedPDK, width: float, length: float, multiplier: int, fingers: int) -> Component:
    CommonSourceTran = Component("CommonSourceTran")
    cstran = nmos(pdk, width=width, length=length, fingers=fingers, multipliers=multiplier, with_dummy=True, with_tie=True, with_substrate_tap=True)
    cstran_ref = prec_ref_center(cstran)
    CommonSourceTran.add(cstran_ref)
    CommonSourceTran.add_ports(cstran_ref.get_ports_list(), prefix="cstran_")
    return CommonSourceTran

#CommonSourceTran(sky130_mapped_pdk, 10, 1, 1, 2).show()

def ResLoad(pdk: MappedPDK) -> Component:
    ResLoad = Component("ResLoad")
    rload = resistor(sky130_mapped_pdk)
    rload_ref = prec_ref_center(rload)
    ResLoad.add(rload_ref)
    ResLoad.add_ports(rload_ref.get_ports_list(), prefix="rload_")
    return ResLoad

#ResLoad(sky130_mapped_pdk).show()

def CommonSourceAmplifier(pdk: MappedPDK) -> Component:
    CommonSourceAmplifier = Component("CommonSourceAmplifier")
    cstran = CommonSourceTran(pdk, 5, 1, 1, 1)
    rload = ResLoad(pdk)
    cstran_ref = prec_ref_center(cstran)
    rload_ref = prec_ref_center(rload)
    CommonSourceAmplifier.add(cstran_ref)
    CommonSourceAmplifier.add(rload_ref)
    movey(rload_ref, evaluate_bbox(cstran_ref)[1] + pdk.util_max_metal_seperation())
    #CommonSourceAmplifier << c_route(pdk, cstran_ref.ports["cstran_A_drain_E"], rload_ref.pprint_ports)
    print(rload_ref)

    return CommonSourceAmplifier

#CommonSourceAmplifier(sky130_mapped_pdk).show()