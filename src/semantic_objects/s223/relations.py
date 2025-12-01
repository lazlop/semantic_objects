from ..core import semantic_object, Predicate as corePredicate
from semantic_mpc_interface import S223, QUDT

# NOTE: not totally happy with declaring domains and ranges this way. Probably better to do it in the entities. I think this is ok for now. 
# Advantage of doing it here: makes entities less of a mixture between object and graph. 
# Disadvantage: Using Strings to specify domains and ranges, rather than classes. Registry concept probbaly not as good as just declaring the valid relatoins in the entities

@semantic_object
class Predicate(corePredicate):
    _ns = S223
@semantic_object
class actuatedByProperty(Predicate):
    pass

@semantic_object
class actuates(Predicate):
    pass

@semantic_object
class cnx(Predicate):
    pass

@semantic_object
class composedOf(Predicate):
    pass

@semantic_object
class connected(Predicate):
    pass

@semantic_object
class connectedFrom(Predicate):
    pass

@semantic_object
class connectedThrough(Predicate):
    pass

@semantic_object
class connectedTo(Predicate):
    pass

@semantic_object
class connectsAt(Predicate):
    pass

@semantic_object
class connectsFrom(Predicate):
    pass

@semantic_object
class connectsThrough(Predicate):
    pass

@semantic_object
class connectsTo(Predicate):
    pass

@semantic_object
class contains(Predicate):
    pass

@semantic_object
class encloses(Predicate):
    pass

@semantic_object
class executes(Predicate):
    pass

@semantic_object
class hasAspect(Predicate):
    pass

@semantic_object
class hasBoundaryConnectionPoint(Predicate):
    pass

@semantic_object
class hasConnectionPoint(Predicate):
    pass

@semantic_object
class hasDeadband(Predicate):
    pass

@semantic_object
class hasDomain(Predicate):
    pass

@semantic_object
class hasDomainSpace(Predicate):
    pass

@semantic_object
class hasElectricalPhase(Predicate):
    pass

@semantic_object
class hasEnumerationKind(Predicate):
    pass

@semantic_object
class hasExternalReference(Predicate):
    pass

@semantic_object
class hasFreezingPoint(Predicate):
    pass

@semantic_object
class hasFrequency(Predicate):
    pass

@semantic_object
class hasInput(Predicate):
    pass

@semantic_object
class hasInternalReference(Predicate):
    pass

@semantic_object
class hasMeasurementResolution(Predicate):
    pass

@semantic_object
class hasMedium(Predicate):
    pass

@semantic_object
class hasMember(Predicate):
    pass

@semantic_object
class hasNumberOfElectricalPhases(Predicate):
    pass

@semantic_object
class hasObservationLocation(Predicate):
    pass

@semantic_object
class hasOptionalConnectionPoint(Predicate):
    pass

@semantic_object
class hasOutput(Predicate):
    pass

@semantic_object
class hasPhysicalLocation(Predicate):
    pass

@semantic_object
class hasProperty(Predicate):
    pass

@semantic_object
class hasReferenceLocation(Predicate):
    pass

@semantic_object
class hasRole(Predicate):
    pass

@semantic_object
class hasSetpoint(Predicate):
    pass

@semantic_object
class hasThermodynamicPhase(Predicate):
    pass

@semantic_object
class hasThreshold(Predicate):
    pass

@semantic_object
class hasAlarmStatus(Predicate):
    pass

@semantic_object
class hasValue(Predicate):
    pass

@semantic_object
class hasVoltage(Predicate):
    pass

@semantic_object
class hasZone(Predicate):
    pass

@semantic_object
class inverseOf(Predicate):
    pass

@semantic_object
class isConnectionPointOf(Predicate):
    pass

@semantic_object
class mapsTo(Predicate):
    pass

@semantic_object
class observes(Predicate):
    pass

@semantic_object
class ofConstituent(Predicate):
    pass

@semantic_object
class ofMedium(Predicate):
    pass

@semantic_object
class ofSubstance(Predicate):
    pass

@semantic_object
class pairedConnectionPoint(Predicate):
    pass

@semantic_object
class hasQuantityKind(Predicate):
    pass

@semantic_object
class hasUnit(Predicate):
    pass