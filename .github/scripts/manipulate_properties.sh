#!/bin/bash
set -e

# Manipulate sample.properties file that the KCL application pulls properties from (ex: streamName, applicationName)
# Depending on the OS, different properties need to be changed
if [[ "$RUNNER_OS" == "macOS" ]]; then
  sed -i "" "s/kclpysample/$STREAM_NAME/g" samples/sample.properties
  sed -i "" "s/PythonKCLSample/$APP_NAME/g" samples/sample.properties
  sed -i "" 's/us-east-5/us-east-1/g' samples/sample.properties
  grep -v "idleTimeBetweenReadsInMillis" samples/sample.properties > samples/temp.properties
  echo "idleTimeBetweenReadsInMillis = 250" >> samples/temp.properties
  mv samples/temp.properties samples/sample.properties
elif [[ "$RUNNER_OS" == "Linux" ]]; then
  sed -i "s/kclpysample/$STREAM_NAME/g" samples/sample.properties
  sed -i "s/PythonKCLSample/$APP_NAME/g" samples/sample.properties
  sed -i 's/us-east-5/us-east-1/g' samples/sample.properties
  sed -i "/idleTimeBetweenReadsInMillis/c\idleTimeBetweenReadsInMillis = 250" samples/sample.properties
elif [[ "$RUNNER_OS" == "Windows" ]]; then
  sed -i "s/kclpysample/$STREAM_NAME/g" samples/sample.properties
  sed -i "s/PythonKCLSample/$APP_NAME/g" samples/sample.properties
  sed -i 's/us-east-5/us-east-1/g' samples/sample.properties
  sed -i "/idleTimeBetweenReadsInMillis/c\idleTimeBetweenReadsInMillis = 250" samples/sample.properties

  echo '@echo off' > samples/run_script.bat
  echo 'python %~dp0\sample_kclpy_app.py %*' >> samples/run_script.bat
  sed -i 's/executableName = sample_kclpy_app.py/executableName = samples\/run_script.bat/' samples/sample.properties
else
  echo "Unknown OS: $RUNNER_OS"
  exit 1
fi

cat samples/sample.properties