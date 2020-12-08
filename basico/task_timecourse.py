import COPASI
from . import model_io
import pandas
import numpy
import logging


def __build_result_from_ts(time_series, use_concentrations=True):
    # type: (COPASI.CTimeSeries) -> pandas.DataFrame
    col_count = time_series.getNumVariables()
    row_count = time_series.getRecordedSteps()

    column_names = []
    column_keys = []
    for i in range(col_count):
        column_keys.append(time_series.getKey(i))
        column_names.append(time_series.getTitle(i))

    concentrations = numpy.empty([row_count, col_count])
    for i in range(row_count):
        for j in range(col_count):
            if use_concentrations: 
                concentrations[i, j] = time_series.getConcentrationData(i, j)
            else:
                concentrations[i, j] = time_series.getData(i, j)

    df = pandas.DataFrame(data=concentrations, columns=column_names)
    df = df.set_index('Time')

    return df


def __method_name_to_type(method_name):
    methods = {
        'deterministic': COPASI.CTaskEnum.Method_deterministic,
        'lsoda': COPASI.CTaskEnum.Method_deterministic,
        'hybridode45': COPASI.CTaskEnum.Method_hybridODE45,
        'hybridlsoda': COPASI.CTaskEnum.Method_hybridLSODA,
        'adaptivesa': COPASI.CTaskEnum.Method_adaptiveSA,
        'tauleap': COPASI.CTaskEnum.Method_tauLeap,
        'stochastic': COPASI.CTaskEnum.Method_stochastic,
        'directMethod': COPASI.CTaskEnum.Method_directMethod,
        'radau5': COPASI.CTaskEnum.Method_RADAU5,
        'sde': COPASI.CTaskEnum.Method_stochasticRunkeKuttaRI5,
    }
    return methods.get(method_name.lower(), COPASI.CTaskEnum.Method_deterministic)


def run_time_course(*args, **kwargs):
    num_args = len(args)
    model = kwargs.get('model', model_io.get_current_model())
    use_initial_values = kwargs.get('use_initial_values', True)

    if 'model' not in kwargs:
        model = model_io.get_current_model()

    task = model.getTask('Time-Course')
    assert (isinstance(task, COPASI.CTrajectoryTask))

    if 'scheduled' in kwargs:
        task.setScheduled(kwargs['scheduled'])

    if 'update_model' in kwargs:
        task.setUpdateModel(kwargs['update_model'])

    if 'method' in kwargs:
        task.setMethodType(__method_name_to_type(kwargs['method']))

    problem = task.getProblem()
    assert (isinstance(problem, COPASI.CTrajectoryProblem))

    if 'duration' in kwargs:
        problem.setDuration(kwargs['duration'])

    if 'automatic' in kwargs:
        problem.setAutomaticStepSize(kwargs['automatic'])

    if 'output_event' in kwargs:
        problem.setOutputEvent(kwargs['output_event'])

    if 'start_time' in kwargs:
        problem.setOutputStartTime(kwargs['start_time'])

    if 'step_number' in kwargs:
        problem.setStepNumber(kwargs['step_number'])

    if 'intervals' in kwargs:
        problem.setStepNumber(kwargs['intervals'])

    if 'stepsize' in kwargs:
        problem.setStepSize(kwargs['stepsize'])

    if num_args == 3:
        problem.setOutputStartTime(args[0])
        problem.setDuration(args[1])
        problem.setStepNumber(args[2])
    elif num_args == 2:
        problem.setDuration(args[0])
        problem.setStepNumber(args[1])
    elif num_args > 0:
        problem.setDuration(args[0])

    problem.setTimeSeriesRequested(True)

    result = task.initializeRaw(COPASI.CCopasiTask.ONLY_TIME_SERIES)
    if not result: 
        logging.error("Error while initializing the simulation: " +  
        COPASI.CCopasiMessage.getLastMessage().getText())
    else: 
        result = task.processRaw(use_initial_values)
        if not result: 
            logging.error("Error while running the simulation: " + 
            COPASI.CCopasiMessage.getLastMessage().getText())

    use_concentrations = kwargs.get('use_concentrations', True)
    if 'use_numbers' in kwargs and kwargs['use_numbers']:
        use_concentrations = False
    
    return __build_result_from_ts(task.getTimeSeries(), use_concentrations)
