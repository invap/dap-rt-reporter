# dap-rt-reporter
Python library to configure, execute the SUT and then report the execution trace

## Dependencies
* GDB version >= 15.1, python support needed to use DAP interpreter (use --with-python=dir when building GDB).

## Usefull links

* https://github.com/tomlin7/debug-adapter-client

## Using docker
1. First build the image
``` sh
docker build . -t dap-rt-reporter-env
```

1. Then
``` sh
docker run  -u `id -u` -it -v$PWD:/home/workspace dap-rt-reporter-env

```
Once in the container:

``` sh
poetry shell
python -m unittest discover -s tests/integration
```

## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
