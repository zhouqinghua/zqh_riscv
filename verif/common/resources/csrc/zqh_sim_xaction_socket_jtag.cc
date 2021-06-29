#include <cstdlib>
#include "zqh_remote_xactionbang.h"

remote_xactionbang_t* xaction_jtag;
extern "C" int jtag_tick
(
 int           jtag_socket_port,
 unsigned char * jtag_TCK,
 unsigned char * jtag_TMS,
 unsigned char * jtag_TDI,
 unsigned char * jtag_TRSTn,
 unsigned char jtag_TDO
)
{
  if (!xaction_jtag) {
    // TODO: Pass in real port number
    xaction_jtag = new remote_xactionbang_t(jtag_socket_port);
  }

  xaction_jtag->tick(jtag_TCK, jtag_TMS, jtag_TDI, jtag_TRSTn, jtag_TDO);

  return xaction_jtag->done() ? (xaction_jtag->exit_code() << 1 | 1) : 0;

}
