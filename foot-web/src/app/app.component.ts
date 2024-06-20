import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import {MatToolbarModule} from '@angular/material/toolbar';
import {MatMenuModule} from '@angular/material/menu';
import {MatButtonModule} from '@angular/material/button';
import { footyService } from '../app/service/footyService.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, RouterOutlet, RouterLink, RouterLinkActive,MatToolbarModule,MatButtonModule, MatMenuModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {
  
  dados?: any[];
  title = 'foot stats';

  constructor(private footyService: footyService, private router: Router) 
  {
    
  }
  
  ngOnInit(): void {
    // initFlowbite();
    
    this.footyService.obterCampeonatos().subscribe(
      (response) => {
        // console.log(response);
        this.dados = response.categorias;
      },
      (error) => {
        console.error('Erro na requisição:', error);
      }
    );
  }
  // ngInit(): void
  // {
  //   initFlowbite();

  // }

  navigateToRoute(routing: string, item: any){

    var navigateTo = '';

    if(routing != "")
      navigateTo = '/' + routing;

    if(item != null && item != '')
      navigateTo += '/' + item.item.id;
    
    this.router.navigate([navigateTo]);
  }
}
