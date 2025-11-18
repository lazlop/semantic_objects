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
    _type = 'actuatedByProperty'

@semantic_object
class actuates(Predicate):
    _type = 'actuates'

@semantic_object
class cnx(Predicate):
    _type = 'cnx'

@semantic_object
class composedOf(Predicate):
    _type = 'composedOf'

@semantic_object
class connected(Predicate):
    _type = 'connected'

@semantic_object
class connectedFrom(Predicate):
    _type = 'connectedFrom'

@semantic_object
class connectedThrough(Predicate):
    _type = 'connectedThrough'

@semantic_object
class connectedTo(Predicate):
    _type = 'connectedTo'

@semantic_object
class connectsAt(Predicate):
    _type = 'connectsAt'

@semantic_object
class connectsFrom(Predicate):
    _type = 'connectsFrom'

@semantic_object
class connectsThrough(Predicate):
    _type = 'connectsThrough'

@semantic_object
class connectsTo(Predicate):
    _type = 'connectsTo'

@semantic_object
class contains(Predicate):
    _type = 'contains'

@semantic_object
class encloses(Predicate):
    _type = 'encloses'

@semantic_object
class executes(Predicate):
    _type = 'executes'

@semantic_object
class hasAspect(Predicate):
    _type = 'hasAspect'

@semantic_object
class hasBoundaryConnectionPoint(Predicate):
    _type = 'hasBoundaryConnectionPoint'

@semantic_object
class hasConnectionPoint(Predicate):
    _type = 'hasConnectionPoint'

@semantic_object
class hasDeadband(Predicate):
    _type = 'hasDeadband'

@semantic_object
class hasDomain(Predicate):
    _type = 'hasDomain'

@semantic_object
class hasDomainSpace(Predicate):
    _type = 'hasDomainSpace'

@semantic_object
class hasElectricalPhase(Predicate):
    _type = 'hasElectricalPhase'

@semantic_object
class hasEnumerationKind(Predicate):
    _type = 'hasEnumerationKind'

@semantic_object
class hasExternalReference(Predicate):
    _type = 'hasExternalReference'

@semantic_object
class hasFreezingPoint(Predicate):
    _type = 'hasFreezingPoint'

@semantic_object
class hasFrequency(Predicate):
    _type = 'hasFrequency'

@semantic_object
class hasInput(Predicate):
    _type = 'hasInput'

@semantic_object
class hasInternalReference(Predicate):
    _type = 'hasInternalReference'

@semantic_object
class hasMeasurementResolution(Predicate):
    _type = 'hasMeasurementResolution'

@semantic_object
class hasMedium(Predicate):
    _type = 'hasMedium'

@semantic_object
class hasMember(Predicate):
    _type = 'hasMember'

@semantic_object
class hasNumberOfElectricalPhases(Predicate):
    _type = 'hasNumberOfElectricalPhases'

@semantic_object
class hasObservationLocation(Predicate):
    _type = 'hasObservationLocation'

@semantic_object
class hasOptionalConnectionPoint(Predicate):
    _type = 'hasOptionalConnectionPoint'

@semantic_object
class hasOutput(Predicate):
    _type = 'hasOutput'

@semantic_object
class hasPhysicalLocation(Predicate):
    _type = 'hasPhysicalLocation'

@semantic_object
class hasProperty(Predicate):
    _type = 'hasProperty'

@semantic_object
class hasReferenceLocation(Predicate):
    _type = 'hasReferenceLocation'

@semantic_object
class hasRole(Predicate):
    _type = 'hasRole'

@semantic_object
class hasSetpoint(Predicate):
    _type = 'hasSetpoint'

@semantic_object
class hasThermodynamicPhase(Predicate):
    _type = 'hasThermodynamicPhase'

@semantic_object
class hasThreshold(Predicate):
    _type = 'hasThreshold'

@semantic_object
class hasAlarmStatus(Predicate):
    _type = 'hasAlarmStatus'

@semantic_object
class hasValue(Predicate):
    _type = 'hasValue'

@semantic_object
class hasVoltage(Predicate):
    _type = 'hasVoltage'

@semantic_object
class hasZone(Predicate):
    _type = 'hasZone'

@semantic_object
class inverseOf(Predicate):
    _type = 'inverseOf'

@semantic_object
class isConnectionPointOf(Predicate):
    _type = 'isConnectionPointOf'

@semantic_object
class mapsTo(Predicate):
    _type = 'mapsTo'

@semantic_object
class observes(Predicate):
    _type = 'observes'

@semantic_object
class ofConstituent(Predicate):
    _type = 'ofConstituent'

@semantic_object
class ofMedium(Predicate):
    _type = 'ofMedium'

@semantic_object
class ofSubstance(Predicate):
    _type = 'ofSubstance'

@semantic_object
class pairedConnectionPoint(Predicate):
    _type = 'pairedConnectionPoint'

@semantic_object
class hasQuantityKind(Predicate):
    _type = 'hasQuantityKind'

@semantic_object
class hasUnit(Predicate):
    _type = 'hasUnit'