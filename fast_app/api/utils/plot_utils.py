import matplotlib.pyplot as plt
import io
from fastapi.responses import StreamingResponse

async def plot_attack_trends(event_service, selected_year):
    try:
        if selected_year:
            
            monthly_data = await event_service.get_monthly_attack_frequency(selected_year)
            months = [data['Month'] for data in monthly_data]
            frequencies_month = [data['Frequency'] for data in monthly_data]
        else:
            
            monthly_data = []
            yearly_data = await event_service.get_yearly_attack_frequency()
            years = [data['Year'] for data in yearly_data]
            frequencies_year = [data['Frequency'] for data in yearly_data]

        
        if monthly_data:
            plt.figure(figsize=(10, 6))
            plt.bar(months, frequencies_month, color='skyblue', label=f'Monthly Frequency ({selected_year})')
            plt.title(f'Monthly Attack Frequency in {selected_year}')
            plt.xlabel('Month')
            plt.ylabel('Frequency')
            plt.xticks(range(1, 13), ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
            plt.grid(True)
            plt.legend()

        if not monthly_data or selected_year is None:
            plt.figure(figsize=(10, 6))
            plt.plot(years, frequencies_year, marker='o', label='Yearly Frequency')
            plt.title('Yearly Attack Frequency')
            plt.xlabel('Year')
            plt.ylabel('Frequency')
            plt.grid(True)
            plt.legend()

 
        img_io = io.BytesIO()
        plt.savefig(img_io, format='png')
        img_io.seek(0)
        plt.close()


        return StreamingResponse(img_io, media_type="image/png")
    
    except Exception as e:
        return {"error": f"An error occurred while generating trends: {str(e)}"}
