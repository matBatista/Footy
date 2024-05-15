using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Configuration;
using Models;
using Models.Model;
using Newtonsoft.Json;
using Services.Interfaces;
using System.Net.Http.Headers;

namespace FootAnalises.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class PartidaController : ControllerBase
    {
        private readonly IConfiguration _configuration;

        private readonly IFootService _footService;
        public PartidaController(IConfiguration configuration, IFootService footService)
        {
            _configuration = configuration;
            _footService = footService;
        }

        [HttpGet]
        [Route("{id_partida}")]
        public async Task<ActionResult> GetRodada(int id_partida)
        {
            ObjectFundamentos list = await _footService.RetornaFundamentos(id_partida);

            return Ok(list);
        }
    }
}
