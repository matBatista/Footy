using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Configuration;
using Models;
using Newtonsoft.Json;
using Services.Interfaces;
using System.Net.Http.Headers;

namespace FootAnalises.Controll
{

    [ApiController]
    [Route("[controller]")]
    public class CampeonatoController : ControllerBase
    {

        private readonly IConfiguration _configuration;

        private readonly IFootService _footService;
        public CampeonatoController(IConfiguration configuration, IFootService footService)
        {
            _configuration = configuration;
            _footService = footService; 
        }
        
        [HttpGet]
        public async Task<ActionResult> GetCampeonatos()
        {
            Campeonato camp = await _footService.RetornaCampeonatos();
            return Ok(camp);
        }

        [HttpGet]
        [Route("camps")]
        public async Task<ActionResult> GetCampeonato()
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
            HttpResponseMessage response = await client.GetAsync(footstats_url + "campeonatos") ;

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

            return Ok(camp);
        }
    }
}
