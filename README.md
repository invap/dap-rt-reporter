# dap-rt-reporter

Python library to configure, execute the SUT and then report the execution trace

## Usefull links

* <https://github.com/tomlin7/debug-adapter-client>

## Using docker

1. First build the image

``` sh
docker build . -t dap-rt-reporter-env
```

2. Then

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

Below a simple example of how to use the library.

```python
from dap_rt_reporter.reporter import Reporter

sut_path = "tests/integration/resources/simple_test/target/debug/simple_test"
log_path = "execute.log"

reporter = Reporter(executable_path=sut_path,
                    execution_trace_log_path=log_path)

source_path = "tests/integration/resources/simple_test/src/main.rs"

reporter.set_checkpoint(
                    source_path=source_path,
                    line=10,
                    before=True,
                    checkpoint_name="test_checkpoint",
                )

reporter.execute()

reporter.stop()
```

To use as a program instead run the following command.

``` sh
python -m dap_rt_reporter --sut sut_binary \
--desc process_descriptor_file --log log_file
```

If the log file already exists you must use -f flag to overwrite it.

In order to run the program you need the following things:

1. A compiled binary with debugging symbols.
2. A csv file with the Structured Sequential Process which is described below.
3. A path to the resulting log.

## Structured Sequential Process description
In order to specify the program Process a file with the following format is needed:

```csv
source:line:before|after,event_type,event_name,*args
```

Each line of the descriptor file represents an event which is correlated with the SUT. The reporter takes as input this descriptor and uses it to output the behavior of the SUT, this log file is then used by the monitor to assert if the behavior matches the modeled behavior.

The events are described by:
1. Source file in which the event happens.
2. Line which correlates with the event.
3. Before|After: indicates if the event should be reported before or after line execution.
4. Event type: current accepted event types are specified below.
5. Event name: name used when reporting.
6. *args: extra arguments used by certain events.

## Contributing

Contributions are what make the open source community such an amazing
place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork
the repo and create a pull request. You can also simply open an
issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
