using Microsoft.Extensions.Configuration;
using Services.Interfaces;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http.Headers;
using System.Text;
using System.Threading.Tasks;

namespace Services.Concretes
{
    public class BaseService : IBaseService
    {
        public IConfiguration _configuration { get;  }

        public BaseService(IConfiguration configuration)
        {
            _configuration = configuration;
        }

        public HttpClient GetHttpClient()
        {
            string footstats_barrear = _configuration["footstats_barrear"];

            HttpClient client = new HttpClient();

            client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Basic", footstats_barrear);

            return client;
        }

    }
}
