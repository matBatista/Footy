using Services.Interfaces;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http.Headers;
using System.Text;
using System.Threading.Tasks;
using Models;
using Microsoft.Extensions.Configuration;
using Newtonsoft.Json;

namespace Services.Concretes
{
    public class FootService : BaseService, IFootService
    {
        public IConfiguration _configuration;

        public FootService(IConfiguration configuration) : base (configuration)
        {
            _configuration = configuration;
        }

        public async Task<Campeonato> RetornaCampeonatos()
        {
            string footstats_barrear = _configuration["footstats_barrear"];
            string footstats_url = _configuration["footstats_url"];
            string resp = "";

            Campeonato camp = new Campeonato();
            // 1. Create an instance of HttpClient
            using HttpClient client = new HttpClient();

            // 2. Set Bearer token in Authorization header
            client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Basic", footstats_barrear);

            // 2. Send HTTP request and handle response
            HttpResponseMessage response = await client.GetAsync(footstats_url + "campeonatos");

            // 3. Check if the request was successful (status code 200)
            if (response.IsSuccessStatusCode)
            {
                // 4. Read response content as string
                string responseBody = await response.Content.ReadAsStringAsync();

                // 5. Deserialize JSON response to object using Newtonsoft.Json
                Object data = JsonConvert.DeserializeObject<Object>(responseBody);

                // 6. Use deserialized data
                resp = $"Received data: {data}";
            }
            else
            {
                resp = $"Failed to retrieve data. Status code: {response.StatusCode}";
            }

            return camp;
        }

    }
}
