start_args=""
if [ -n "${BIND_IP}" ]; then
  start_args="${start_args} --bind_ip ${BIND_IP}"
fi
if [ -n "${BIND_PORT}" ]; then
  start_args="${start_args} --bind_port ${BIND_PORT}"
fi
if [ -n "${DNS_IP}" ]; then
  start_args="${start_args} --dns_ip ${DNS_IP}"
fi
if [ -n "${DNS_PORT}" ]; then
  start_args="${start_args} --dns_port ${DNS_PORT}"
fi
if [ -n "${SMART_MODE}" ]; then
  start_args="${start_args} --smart"
fi
if [ -n "${REDIS_URI}" ]; then
  start_args="${start_args} --redis_uri ${REDIS_URI}"
fi
if [ -n "${SNI_IP}" ]; then
  start_args="${start_args} --sni_ip ${SNI_IP}"
fi
if [ -n "${AGGRESSIVE_MODE}" ]; then
  start_args="${start_args} --aggressive"
fi
if [ -n "${SNI_TTL}" ]; then
  start_args="${start_args} --sni_ttl ${SNI_TTL}"
fi
if [ -n "${INQUIRY_TTL}" ]; then
  start_args="${start_args} --inquiry_ttl ${INQUIRY_TTL}"
fi
if [ -n "${NO_INQUIRER}" ]; then
  start_args="${start_args} --no_inquirer ${NO_INQUIRER}"
fi
if [ -n "${LOG_LEVEL}" ]; then
  start_args="${start_args} --log ${LOG_LEVEL}"
fi

python server.py ${start_args}
