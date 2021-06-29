#include <fesvr/dtm.h>
class sb_dtm_t : public dtm_t
{
 public:
  sb_dtm_t(int argc, char**argv);
  ~sb_dtm_t();

 private:
  uint32_t new_xlen = 64;
  void read_chunk(addr_t taddr, size_t len, void* dst) override;
  void write_chunk(addr_t taddr, size_t len, const void* src) override;
  void clear_chunk(addr_t taddr, size_t len) override;
};
