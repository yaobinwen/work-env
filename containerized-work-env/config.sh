GIT_USER_EMAIL="robin.wyb@gmail.com"
GIT_USER_NAME="Yaobin Wen"
USER_NAME="ywen"

CID="$(cat "/tmp/cid.containerized-work-env-personal")" || return
echo "$CID ansible_user=root ansible_python_interpreter=auto" \
    >"inventory" || return

ansible-playbook -vv -c docker -i "inventory" \
  -e "git_user_email='$GIT_USER_EMAIL'" \
  -e "git_user_full_name='$GIT_USER_NAME'" \
  -e "unprivileged_user_name='$USER_NAME'" \
  "containerized-work-env.yml" || return
