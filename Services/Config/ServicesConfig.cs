using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Microsoft.Extensions.DependencyInjection;
using Services.Concretes;
using Services.Interfaces;

namespace Services.Config
{
    public static class ServicesConfig
    {
        public static IServiceCollection AddServices(this IServiceCollection services) 
        {
            services.AddScoped<IFootService, FootService>();

            return services;
        }

    }
}
