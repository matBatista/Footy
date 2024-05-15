using Microsoft.Extensions.Configuration;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Services.Concretes
{
    public class BaseService
    {
        public IConfiguration _configuration { get;  }

        public BaseService(IConfiguration configuration)
        {
            _configuration = configuration;
        }

    }
}
