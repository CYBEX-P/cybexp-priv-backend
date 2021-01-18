#!/usr/bin/env bash

DIR_PATH=`dirname $0`
FULL_PATH=`readlink --canonicalize $DIR_PATH`


DOCKERFILE_LOC=$FULL_PATH

OG_ARGUMENTS="$@" # in case we need to exec when starting docker

if [ "`id -u`" -eq "0" ]; then
   echo "Not recomended to run ar root. Continuing anyways..."
fi
if [[ "`groups`" == *"docker"* || "`id -u`" -eq "0" ]]; then
      DOCKER_COMPOSE="docker-compose"
   else
      DOCKER_COMPOSE="sudo -E docker-compose"

fi


function print_help {
   echo
   echo 'Manipulate docker-compose to start and stop priv-backend-api and DB servives. By default the container are left behind,'
   echo 'vacuum recommended. Build at least once or when code has changed.'
   echo
   echo -e 'Usage:'
   echo -e "  $0"' [Options] config-file'
   echo -e "  $0"' --build --build-only'
   echo 
   echo -e 'Positional arguments:'
   echo -e '  config-file\t\tconfiguration file yaml'
   echo
   echo -e 'Options arguments:'
   echo -e '  -b, --build\t\tbuild docker image'
   echo -e '  --build-only\t\texit after building'
   # echo -e '  -s, --shell\t\trun shell, ignores most flags'

   echo -e '  --keep-orphan\t\tkeep orphans (default: removed them)'
   # echo -e '  --shell-no-db\t\tdo not run the db service when the --shell is specified'

   echo -e '  -c, --vacuum\t\tremove containers upon exit. If more than one container'
   echo -e '              \t\tof this type exists, it will remove all'
   # echo -e '  --bind [IFACE:]PORT'
   # echo -e '              \t\tinterface and/or port to bind to (eg 192.168.1.100:8080)(default: 5001)'

   echo -e '  -h, --help\t\tprint this help'


   echo 
}

function build_image {
   # export "BIND_INTERFACE=$BIND_IFACE_PORT"

   pushd $DIR_PATH > /dev/null 2>&1 # supress output
   $DOCKER_COMPOSE build
   popd > /dev/null 2>&1 # supress output
}

function run_image {
   pushd $DIR_PATH > /dev/null 2>&1 # supress output
   echo "config file: $CONFIG_FILE_P"
   export "CONFIG_FILE=$CONFIG_FILE_P"
   # export "BIND_INTERFACE=$BIND_IFACE_PORT"

   $DOCKER_COMPOSE up $REMOVE_ORPHANS
   # $DOCKER_COMPOSE stop $REMOVE_ORPHANS > /dev/null  2>&1 # supress output

   popd > /dev/null 2>&1 # supress output

}
# function run_shell {
#    pushd $DIR_PATH > /dev/null 2>&1 # supress output
#    echo "config file: $CONFIG_FILE_P"
#    export "CONFIG_FILE=$CONFIG_FILE_P"
#    if [ -z "${SHELL_DRUN_DB+set}" ]; then
#       $DOCKER_COMPOSE up -d priv-backend-db
#    fi
#    echo hey
#    $DOCKER_COMPOSE run priv-backend-api --entrypoint bash
#    $DOCKER_COMPOSE stop
#    popd > /dev/null 2>&1 # supress output


# }
function remove_container {
   pushd $DIR_PATH > /dev/null 2>&1 # supress output

   export "CONFIG_FILE=$CONFIG_FILE_P"
   export "BIND_INTERFACE=$BIND_IFACE_PORT"

   $DOCKER_COMPOSE down $REMOVE_ORPHANS

   popd > /dev/null 2>&1 # supress output

}

#flags
BUILD_IT=0
BUILD_ONLY=0
SHELL_ONLY=0
CLEANUP=0
BIND_IFACE_PORT="5001"

REMOVE_ORPHANS="--remove-orphans" 

POSITIONAL=""
while (( "$#" )); do
   case "$1" in
      -h|--help)
         print_help
         exit 0
         ;;
      -b|--build)
         BUILD_IT=1
         shift
         ;;
      --build-only)
         BUILD_ONLY=1
         shift
         ;;
      # -s|--shell)
      #    SHELL_ONLY=1
      #    shift
      #    ;;
      -c|--vacuum)
         CLEANUP=1
         shift
         ;;
      --keep-orphan)
         REMOVE_ORPHANS=""
         shift
         ;;
      # --shell-no-db)
      #    SHELL_DRUN_DB=1
      #    shift
      #    ;;
      # --bind)
      #    if [ -n "$2" ] && [ ${2:0:1} != "-" ]; then
      #       BIND_IFACE_PORT=$2
      #       shift 2
      #    else
      #       echo "Error: Argument for $1 is missing" >&2
      #       print_help
      #       exit 1
      #    fi
      #    ;;
      -*|--*=) # unsupported flags
         echo "Error: Unsupported flag $1" >&2
         exit 1
         ;;
      *) # preserve positional arguments
         POSITIONAL="$POSITIONAL $1"
         shift
         ;;
   esac
done
# set positional arguments in their proper place
eval set -- "$POSITIONAL"
if [ "$#" -eq 1 ] && [ $BUILD_ONLY -eq 0 ]; then
   CONFIG_FILE_P=`realpath $1`
   shift 1
elif [ $BUILD_ONLY -eq 0 ];then
   # echo $#
   # echo $POSITIONAL
   echo "Error: Missing positional arguments." >&2
   print_help
   exit 2
fi

DOCKER_STATE=`systemctl status docker | grep Active: | head -n 1 | awk '{print $2}'`

if [ "$DOCKER_STATE" = "inactive" ]; then
   echo "Starting docker service..."
   sudo systemctl start docker
   exec $0 $OG_ARGUMENTS
fi

if [ $BUILD_IT -eq 1 ]; then
   build_image
   if [ $? -ne 0 ]; then
      echo "Error: Failed to build image" >&2
      exit 3
   fi
fi
if [ $BUILD_ONLY -eq 1 ]; then
   exit 0
fi


if [ "$DOCKER_STATE" = "active" ]; then
   if [ $SHELL_ONLY -eq 1 ]; then
      run_shell
   else
      run_image
   fi

   if [ $CLEANUP -eq 1 ]; then
      remove_container
   fi

else
   echo 'Failed to start docker, please start it.' >&2
   exit 1
fi





# parse yaml file 
# https://stackoverflow.com/a/21189044/12044480