# dap-rt-reporter

Python library to configure, execute the SUT and then report the execution trace

## Useful links

* <https://github.com/tomlin7/debug-adapter-client>

## Using docker

1. First build the image

    ``` sh
    docker build . -t dap-rt-reporter-env
    ```

1. Then

    ``` sh
    docker run -it -v$PWD:/home/workspace dap-rt-reporter-env
    ```

    To execute the unit tests, in the container:

    ``` sh
    poetry shell
    python -m unittest discover -s tests/integration
    ```

    To execute the program:

    ``` sh
    poetry shell
    python -m dap_rt_reporter\
      --sut tests/integration/resources/simple_test/target/debug/simple_test \
      --desc tests/integration/resources/simple_test_config.csv --log execute.log
    ```

## Usage

The project can be used as a library which you can use to add events
programmatically, as shown below.

```python
from dap_rt_reporter.reporter import Reporter

# Binary and log paths
sut_path = "tests/integration/resources/simple_test/target/debug/simple_test"
log_path = "execute.log"

# Initialize reporter
reporter = Reporter(executable_path=sut_path,
                    execution_trace_log_path=log_path)

source_path = "tests/integration/resources/simple_test/src/main.rs"

# Set checkpoint event in line 10
reporter.set_checkpoint(
                    source_path=source_path,
                    line=10,
                    before=True,
                    checkpoint_name="test_checkpoint",
                )

# Set variable value assign event in line 8, reads the value of 'x'
reporter.set_variable_value_assign(
                    source_path=source_path,
                    line=12,
                    before=False,
                    vva_name="var_x",
                    variable="x"
                    )

# Start program execution and reporting
reporter.execute()

reporter.close()
```

It can also be used as a program instead, to run use the following command.

``` sh
python -m dap_rt_reporter --sut sut_binary \
--desc process_descriptor_file --log log_file
```

In order to run the program you need the following things:

1. A compiled binary with debugging symbols.
1. A csv file with the execution report specification which is described below.
1. A path to the resulting log. If the log file already exists you must use -f
flag to overwrite it.

## Execution report specification

In order to specify the program execution a file with the following format is needed:

```csv
[SOURCE]:[LINE]:[b|a],[EVENT],[EVENT_NAME],[*ARGS]
```

Each line of the descriptor file represents an event which is correlated with the SUT. The reporter takes as input this descriptor and uses it to output the behavior of the SUT, this log file is then used by the monitor to assert if the behavior matches the modeled behavior.

The events are described by:

1. SOURCE: Source file in which the event happens.
1. LINE: Line which correlates with the event.
1. Before|After: indicates if the event should be reported before or after line execution.
1. EVENT: current accepted events are specified below.
1. EVENT_NAME: name used when reporting.
1. *ARGS: extra arguments used by certain events (currently only variable_value_assign).

### Events

The currently supported events are:

1. checkpoint_reached: Represents arriving at a checkpoint.

    ```csv
    source:6:b,checkpoint_reached,chk_0
    ```

1. task_started: Marks the beginning of a task.

    ```csv
    source:8:b,task_started,init
    ```

1. task_finished: Marks the end of a task.

    ```csv
    source:15:b,source:11:b,task_finished,init
    ```

1. variable_value_assign: Check the value of a variable or expression
in current stack frame.

    ```csv
    source:13:b,variable_value_assign,var_x,x
    ```

The resulting log after running all above events looks like this:

```csv
1732838404820600,process_event,checkpoint_reached,chk_0
1732838404825209,process_event,task_started,init
1732838404829541,process_event,task_finished,init
1732838406839570,state_event,variable_value_assign,var_x,145
```

The output format contains:

```csv
[TIMESTAMP],[EVENT_TYPE],[EVENT],[EVENT_NAME],[*ARGS]
```

1. TIMESTAMP: The moment in which the event took place in microseconds since epoch.
1. EVENT_TYPE: The type of event (process, state).
1. EVENT: The event in question as described above.
1. EVENT_NAME: The name used to report the event.
1. *ARGS: Extra arguments used for the event.

## Contributing

Contributions are what make the open source community such an amazing
place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork
the repo and create a pull request. You can also simply open an
issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
1. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
1. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
1. Push to the Branch (`git push origin feature/AmazingFeature`)
1. Open a Pull Request
