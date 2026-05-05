from nicegui import ui, app
import httpx

BASE_URL = "http://localhost:8000"
USER_ID = "123"

async def add_site(site_input, refresh_fn):
    url = site_input.value.strip()
    if not url:
        ui.notify('Enter URL here', type='warning')
        return
    async with httpx.AsyncClient() as client:
        await client.post(f'{BASE_URL}/blocker/sites/{USER_ID}', params={'url': url})
    site_input.value = ''
    await refresh_fn()
    ui.notify(f'Blocked: {url}', type='positive')

async def remove_site(url, refresh_fn):
    async with httpx.AsyncClient() as client:
        await client.delete(f'{BASE_URL}/blocker/sites/{USER_ID}/{url}')
    await refresh_fn()
    ui.notify(f'Unblocked: {url}', type='info')

@ui.page('/')
async def main():
    ui.label('Distraction Blocker')
    with ui.card().classes('w-96'):
        site_input = ui.input(placeholder='e.g. what.com').classes('w-full')
        ui.button('Block Site', on_click=lambda: add_site(site_input, refresh_list))
    ui.separator().classes('q-my-md')
    ui.label('BLOCKED SITES LISTED BELOW')
    site_list = ui.column()

    async def refresh_list():
        site_list.clear()
        async with httpx.AsyncClient() as client:
            res = await client.get(f'{BASE_URL}/blocker/sites/{USER_ID}')
            sites = res.json()
        with site_list:
            if not sites:
                ui.label('No sites blocked yet').classes('text-caption text-grey')
            for site in sites:
                with ui.row().classes('items-center gap-4'):
                    ui.label(site).classes('text-body1')
                    ui.button('Remove', on_click=lambda s=site: remove_site(s, refresh_list), color='red-5').props('flat dense')

    await refresh_list()
    ui.add_head_html("""
    <script>
      window.addEventListener('beforeunload', function(e) {
        e.preventDefault();
        e.returnValue = '';
      });
    </script>
    """)


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(port=8080)
