import { Component, inject } from '@angular/core';
import { Router, RouterOutlet } from '@angular/router';
import { SquadDialogComponent } from './dialog/squadDialogComponent.component';
import { MatDialog } from '@angular/material/dialog';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {
  title = 'foot-stats';

  readonly dialog = inject(MatDialog);
  
  constructor(private router: Router) 
  {
    
  }
  

  openModal(){
    const dialogRef = this.dialog.open(SquadDialogComponent, {
      width: '980px',
      height: '600px',
      maxHeight: '90vh',
      maxWidth: '90vw',
      // data: {id_time_a: item.partida.mandante.id, id_time_b: item.partida.visitante.id, id_campeonato: this.id_campeonato}
    });
  }
}


