from . import model_io
import pandas
import COPASI
import collections


def __status_to_int(status):
    # type: (str)->int
    codes = {
        "fixed": COPASI.CModelEntity.Status_FIXED,
        "assignment": COPASI.CModelEntity.Status_ASSIGNMENT,
        "ode": COPASI.CModelEntity.Status_ODE,
        "reactions": COPASI.CModelEntity.Status_REACTIONS,
        "time": COPASI.CModelEntity.Status_TIME,
    }
    return codes.get(status, COPASI.CModelEntity.Status_FIXED)


def __status_to_string(status):
    # type: (int)->str
    strings = {
        COPASI.CModelEntity.Status_FIXED: "fixed",
        COPASI.CModelEntity.Status_ASSIGNMENT: "assignment",
        COPASI.CModelEntity.Status_ODE: "ode",
        COPASI.CModelEntity.Status_REACTIONS: "reactions",
        COPASI.CModelEntity.Status_TIME: "time",
    }
    return strings.get(status, 'fixed')


def get_species(name=None, **kwargs):
    # type: () -> pandas.DataFrame
    dm = kwargs.get('model', model_io.get_current_model())
    assert (isinstance(dm, COPASI.CDataModel))

    model = dm.getModel()
    assert (isinstance(model, COPASI.CModel))

    metabs = model.getMetabolitesX()
    assert(isinstance(metabs, COPASI.MetabVector))

    num_metabs = metabs.size()
    data = []

    for i in range(num_metabs):
        metab = metabs.get(i)
        assert (isinstance(metab, COPASI.CMetab))

        unit = metab.getUnitExpression()
        if not unit:
            unit = model.getQuantityUnit() + '/' + model.getVolumeUnit()

        metab_data = {
            'name': metab.getObjectName(),
            'compartment': metab.getCompartment().getObjectName(),
            'type': __status_to_string(metab.getStatus()),
            'unit': unit,
            'initial_concentration': metab.getInitialConcentration(),
            'initial_particle_number': metab.getInitialValue(),
            'initial_expression': metab.getInitialExpression(),
            'expression': metab.getExpression(),
            'concentration': metab.getConcentration(),
            'particle_number': metab.getValue(),
            'rate': metab.getRate(),
            'key': metab.getKey(),
        }

        if 'name' in kwargs and not kwargs['name'] in metab_data['name']:
            continue

        if name and name not in metab_data['name']:
            continue

        if 'compartment' in kwargs and not kwargs['compartment'] in metab_data['compartment']:
            continue

        if 'type' in kwargs and kwargs['type'] not in metab_data['type']:
            continue

        data.append(metab_data)

    if not data:
        return None

    return pandas.DataFrame(data=data).set_index('name')


def get_compartments(name=None, **kwargs):
    # type: () -> pandas.DataFrame
    dm = kwargs.get('model', model_io.get_current_model())
    assert (isinstance(dm, COPASI.CDataModel))

    model = dm.getModel()
    assert (isinstance(model, COPASI.CModel))

    compartments = model.getCompartments()
    assert(isinstance(compartments, COPASI.CompartmentVectorNS))

    num_compartments = compartments.size()
    data = []

    for i in range(num_compartments):
        compartment = compartments.get(i)
        assert (isinstance(compartment, COPASI.CCompartment))

        unit = compartment.getUnitExpression()
        if not unit:
            unit = model.getVolumeUnit()

        comp_data = {
            'name': compartment.getObjectName(),
            'type': __status_to_string(compartment.getStatus()),
            'unit': unit,
            'initial_size': compartment.getInitialValue(),
            'initial_expression': compartment.getInitialExpression(),
            'expression': compartment.getExpression(),
            'size': compartment.getValue(),
            'rate': compartment.getRate(),
            'key': compartment.getKey(),
        }

        if 'name' in kwargs and kwargs['name'] not in comp_data['name']:
            continue

        if name and name not in comp_data['name']:
            continue

        if 'type' in kwargs and kwargs['type'] not in comp_data['type']:
            continue

        data.append(comp_data)

    if not data:
        return None

    return pandas.DataFrame(data=data).set_index('name')


def get_parameters(name=None, **kwargs):
    # type: () -> pandas.DataFrame
    dm = kwargs.get('model', model_io.get_current_model())
    assert (isinstance(dm, COPASI.CDataModel))

    model = dm.getModel()
    assert (isinstance(model, COPASI.CModel))

    parameters = model.getModelValues()
    assert(isinstance(parameters, COPASI.ModelValueVectorN))

    num_params = parameters.size()
    data = []

    for i in range(num_params):
        param = parameters.get(i)
        assert (isinstance(param, COPASI.CModelValue))

        unit = param.getUnitExpression()
        if 'unit' in kwargs and not kwargs['unit'] in unit:
            continue

        param_data = {
            'name': param.getObjectName(),
            'type': __status_to_string(param.getStatus()),
            'unit': unit,
            'initial_value': param.getInitialValue(),
            'initial_expression': param.getInitialExpression(),
            'expression': param.getExpression(),
            'value': param.getValue(),
            'rate': param.getRate(),
            'key': param.getKey(),
        }

        if 'name' in kwargs and kwargs['name'] not in param_data['name']:
            continue

        if name and name not in param_data['name']:
            continue

        if 'type' in kwargs and kwargs['type'] not in param_data['type']:
            continue

        data.append(param_data)

    if not data:
        return None

    return pandas.DataFrame(data=data).set_index('name')


def get_reactionParameters(name=None, **kwargs):
    dm = kwargs.get('model', model_io.get_current_model())
    assert (isinstance(dm, COPASI.CDataModel))

    model = dm.getModel()
    assert (isinstance(model, COPASI.CModel))

    reactions = model.getReactions()

    num_reactions = reactions.size()
    data = []

    for i in range(num_reactions):
        reaction = reactions.get(i)

        parameterGroup = reaction.getParameters()
        num_params = parameterGroup.size()

        for j in range(num_params):
            parameter = parameterGroup.getParameter(j)

            param_data = {
                'name': parameter.getObjectDisplayName(),
                'value': parameter.getValue(),
                'reaction name' : reaction.getObjectName()
            }

            if 'name' in kwargs and kwargs['name'] not in param_data['name']:
                continue

            if name and name not in param_data['name']:
                continue

            if 'type' in kwargs and kwargs['type'] not in param_data['type']:
                continue

            data.append(param_data)

    if not data:
        return None

    return pandas.DataFrame(data=data).set_index('reaction name')


def get_reactions(name=None, **kwargs):
    dm = kwargs.get('model', model_io.get_current_model())
    assert (isinstance(dm, COPASI.CDataModel))

    model = dm.getModel()
    assert (isinstance(model, COPASI.CModel))

    reactions = model.getReactions()

    num_reactions = reactions.size()
    data = []

    for i in range(num_reactions):
        reaction = reactions.get(i)

        reaction_data = {
            'scheme': reaction.getReactionScheme(),
            'name': reaction.getObjectName()
        }

        if 'name' in kwargs and kwargs['name'] not in reaction_data['name']:
            continue

        if name and name not in reaction_data['name']:
            continue

        if 'type' in kwargs and kwargs['type'] not in reaction_data['type']:
            continue

        data.append(reaction_data)

    if not data:
        return None

    return pandas.DataFrame(data=data).set_index('name')

def get_timeUnit(name=None, **kwargs):
    dm = kwargs.get('model', model_io.get_current_model())
    assert (isinstance(dm, COPASI.CDataModel))

    model = dm.getModel()
    assert (isinstance(model, COPASI.CModel))

    time = model.getTimeUnit()

    return time

def set_parameters(name=None, **kwargs):
    dm = kwargs.get('model', model_io.get_current_model())
    assert (isinstance(dm, COPASI.CDataModel))

    model = dm.getModel()
    assert (isinstance(model, COPASI.CModel))

    parameters = model.getModelValues()
    assert (isinstance(parameters, COPASI.ModelValueVectorN))

    num_params = parameters.size()

    for i in range(num_params):
        param = parameters.get(i)
        assert (isinstance(param, COPASI.CModelValue))
        current_name = param.getObjectName()

        if 'name' in kwargs and kwargs['name'] not in current_name:
            continue

        if name and type(name) is str and name not in current_name:
            continue

        if name and isinstance(name, collections.Iterable) and current_name not in name:
            continue

        if 'unit' in kwargs:
            param.setUnitExpression(kwargs['unit'])

        if 'initial_value' in kwargs:
            param.setInitialValue(kwargs['initial_value'])

        if 'initial_expression' in kwargs:
            param.setInitialExpression(kwargs['initial_expression'])

        if 'expression' in kwargs:
            param.setExpression(kwargs['expression'])

        if 'status' in kwargs:
            param.setStatus(__status_to_int(kwargs['status']))

        if 'type' in kwargs:
            param.setStatus(__status_to_int(kwargs['type']))



def set_reactionParameters(name=None, **kwargs):
    dm = kwargs.get('model', model_io.get_current_model())
    assert (isinstance(dm, COPASI.CDataModel))

    model = dm.getModel()
    assert (isinstance(model, COPASI.CModel))

    reactions = model.getReactions()
    num_reactions = reactions.size()

    for i in range(num_reactions):
        reaction = reactions.get(i)

        parameterGroup = reaction.getParameters()
        num_params = parameterGroup.size()

        for j in range(num_params):
            param = parameterGroup.getParameter(j)

            current_name = param.getObjectDisplayName()

            if 'name' in kwargs and kwargs['name'] not in current_name:
                continue

            if name and type(name) is str and name not in current_name:
                continue

            if name and isinstance(name, collections.Iterable) and current_name not in name:
                continue

            if 'new_name' in kwargs:
                param.setObjectName(kwargs['new_name'])

            if 'value' in kwargs:
                param.setDblValue(kwargs['value'])


def set_reaction(name=None, **kwargs):
    dm = kwargs.get('model', model_io.get_current_model())
    assert (isinstance(dm, COPASI.CDataModel))

    model = dm.getModel()
    assert (isinstance(model, COPASI.CModel))

    reactions = model.getReactions()
    num_reactions = reactions.size()

    for i in range(num_reactions):
        reaction = reactions.get(i)

        current_name = reaction.getObjectName()

        if 'name' in kwargs and kwargs['name'] not in current_name:
            continue

        if name and type(name) is str and name not in current_name:
            continue

        if name and isinstance(name, collections.Iterable) and current_name not in name:
            continue

        if 'new_name' in kwargs:
            reaction.setObjectName(kwargs['new_name'])

        if 'scheme' in kwargs:
            reaction.setReactionScheme(kwargs['scheme'])


def set_species(name=None, **kwargs):
    dm = kwargs.get('model', model_io.get_current_model())
    assert (isinstance(dm, COPASI.CDataModel))

    model = dm.getModel()
    assert (isinstance(model, COPASI.CModel))

    metabs = model.getMetabolitesX()
    num_metabs = metabs.size()

    set = COPASI.ObjectStdVector()

    for i in range(num_metabs):
        metab = metabs.get(i)
        assert (isinstance(metab, COPASI.CMetab))

        current_name = metab.getObjectName()

        if 'name' in kwargs and kwargs['name'] not in current_name:
            continue

        if name and type(name) is str and name not in current_name:
            continue

        if name and isinstance(name, collections.Iterable) and current_name not in name:
            continue

        if 'new_name' in kwargs:
            metab.setObjectName(kwargs['new_name'])

        if 'unit' in kwargs:
            metab.setUnitExpression(kwargs['unit'])

        if 'initial_concentration' in kwargs:
            metab.setInitialConcentration(kwargs['initial_concentration'])
            set.append(metab.getInitialConcentrationReference())

        if 'initial_particle_number' in kwargs:
            metab.setInitialValue(kwargs['initial_particle_number']),
            set.append(metab.getInitialValueReference())

        if 'initial_expression' in kwargs:
            metab.setInitialExpression(kwargs['initial_expression'])

        if 'expression' in kwargs:
            metab.setExpression(kwargs['expression'])

    model.updateInitialValues(set)


def set_timeUnit(name=None, **kwargs):
    dm = kwargs.get('model', model_io.get_current_model())
    assert (isinstance(dm, COPASI.CDataModel))

    model = dm.getModel()
    assert (isinstance(model, COPASI.CModel))

    c_unit = COPASI.CUnit(kwargs['unit'])
    if c_unit.isUnitType(COPASI.CUnit.time) is False:
        print ('The unit \'{}\' is not supported.'.format(kwargs['unit']))
        return

    if 'unit' in kwargs:
       assert (isinstance((kwargs['unit']), str))

       c_unit = COPASI.CUnit(kwargs['unit'])

       if c_unit.isUnitType(COPASI.CUnit.time):
           model.setTimeUnit(kwargs['unit'])

       else:
        print ('The unit \'{}\' is not supported.'.format(kwargs['unit']))

