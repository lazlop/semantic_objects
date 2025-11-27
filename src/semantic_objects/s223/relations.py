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
    _name = 'actuatedByProperty'

@semantic_object
class actuates(Predicate):
    _name = 'actuates'

@semantic_object
class cnx(Predicate):
    _name = 'cnx'

@semantic_object
class composedOf(Predicate):
    _name = 'composedOf'

@semantic_object
class connected(Predicate):
    _name = 'connected'

@semantic_object
class connectedFrom(Predicate):
    _name = 'connectedFrom'

@semantic_object
class connectedThrough(Predicate):
    _name = 'connectedThrough'

@semantic_object
class connectedTo(Predicate):
    _name = 'connectedTo'

@semantic_object
class connectsAt(Predicate):
    _name = 'connectsAt'

@semantic_object
class connectsFrom(Predicate):
    _name = 'connectsFrom'

@semantic_object
class connectsThrough(Predicate):
    _name = 'connectsThrough'

@semantic_object
class connectsTo(Predicate):
    _name = 'connectsTo'

@semantic_object
class contains(Predicate):
    _name = 'contains'

@semantic_object
class encloses(Predicate):
    _name = 'encloses'

@semantic_object
class executes(Predicate):
    _name = 'executes'

@semantic_object
class hasAspect(Predicate):
    _name = 'hasAspect'

@semantic_object
class hasBoundaryConnectionPoint(Predicate):
    _name = 'hasBoundaryConnectionPoint'

@semantic_object
class hasConnectionPoint(Predicate):
    _name = 'hasConnectionPoint'

@semantic_object
class hasDeadband(Predicate):
    _name = 'hasDeadband'

@semantic_object
class hasDomain(Predicate):
    _name = 'hasDomain'

@semantic_object
class hasDomainSpace(Predicate):
    _name = 'hasDomainSpace'

@semantic_object
class hasElectricalPhase(Predicate):
    _name = 'hasElectricalPhase'

@semantic_object
class hasEnumerationKind(Predicate):
    _name = 'hasEnumerationKind'

@semantic_object
class hasExternalReference(Predicate):
    _name = 'hasExternalReference'

@semantic_object
class hasFreezingPoint(Predicate):
    _name = 'hasFreezingPoint'

@semantic_object
class hasFrequency(Predicate):
    _name = 'hasFrequency'

@semantic_object
class hasInput(Predicate):
    _name = 'hasInput'

@semantic_object
class hasInternalReference(Predicate):
    _name = 'hasInternalReference'

@semantic_object
class hasMeasurementResolution(Predicate):
    _name = 'hasMeasurementResolution'

@semantic_object
class hasMedium(Predicate):
    _name = 'hasMedium'

@semantic_object
class hasMember(Predicate):
    _name = 'hasMember'

@semantic_object
class hasNumberOfElectricalPhases(Predicate):
    _name = 'hasNumberOfElectricalPhases'

@semantic_object
class hasObservationLocation(Predicate):
    _name = 'hasObservationLocation'

@semantic_object
class hasOptionalConnectionPoint(Predicate):
    _name = 'hasOptionalConnectionPoint'

@semantic_object
class hasOutput(Predicate):
    _name = 'hasOutput'

@semantic_object
class hasPhysicalLocation(Predicate):
    _name = 'hasPhysicalLocation'

@semantic_object
class hasProperty(Predicate):
    _name = 'hasProperty'

@semantic_object
class hasReferenceLocation(Predicate):
    _name = 'hasReferenceLocation'

@semantic_object
class hasRole(Predicate):
    _name = 'hasRole'

@semantic_object
class hasSetpoint(Predicate):
    _name = 'hasSetpoint'

@semantic_object
class hasThermodynamicPhase(Predicate):
    _name = 'hasThermodynamicPhase'

@semantic_object
class hasThreshold(Predicate):
    _name = 'hasThreshold'

@semantic_object
class hasAlarmStatus(Predicate):
    _name = 'hasAlarmStatus'

@semantic_object
class hasValue(Predicate):
    _name = 'hasValue'

@semantic_object
class hasVoltage(Predicate):
    _name = 'hasVoltage'

@semantic_object
class hasZone(Predicate):
    _name = 'hasZone'

@semantic_object
class inverseOf(Predicate):
    _name = 'inverseOf'

@semantic_object
class isConnectionPointOf(Predicate):
    _name = 'isConnectionPointOf'

@semantic_object
class mapsTo(Predicate):
    _name = 'mapsTo'

@semantic_object
class observes(Predicate):
    _name = 'observes'

@semantic_object
class ofConstituent(Predicate):
    _name = 'ofConstituent'

@semantic_object
class ofMedium(Predicate):
    _name = 'ofMedium'

@semantic_object
class ofSubstance(Predicate):
    _name = 'ofSubstance'

@semantic_object
class pairedConnectionPoint(Predicate):
    _name = 'pairedConnectionPoint'

@semantic_object
class hasQuantityKind(Predicate):
    _name = 'hasQuantityKind'

@semantic_object
class hasUnit(Predicate):
    _name = 'hasUnit'