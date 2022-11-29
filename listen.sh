set -e
set -x

if [ "$1" == start ]; then
  if tmux has-session -t yptools; then
    echo "tool_listen is exist ,restart it!"
    tmux kill-session -t yptools
  fi
  tmux new-session -d -s yptools
  tmux send-keys -t "yptools" C-z 'python main.py' Enter
  echo "yptools on : host:8087"
elif [ "$1" == stop ]; then
  if tmux has-session -t yptools; then
    tmux kill-session -t yptools
  fi
  echo "yptools is stop"
else
  echo "unknown arg $1"
fi
