import { expect, test } from '@playwright/test';
import { awaitResponse, checkOpenTaskpane, clickButtonAndAwaitResponse, closeTaskpane, getMitoFrameWithTestCSV } from '../utils';


test.describe('Pivot Table', () => {

    test('Allows Editing When Reopened', async ({ page }) => {
        const mito = await getMitoFrameWithTestCSV(page);
        
        await clickButtonAndAwaitResponse(page, mito, { name: 'Pivot' })
        
        await checkOpenTaskpane(mito, 'Create Pivot Table test_pivot');

        // Check new empty tab
        await mito.getByText('test_pivot', { exact: true }).click();
        await expect(mito.getByText('test_pivot', { exact: true })).toBeVisible();
        await expect(mito.getByText('No data in dataframe.')).toBeVisible();
        
        // Add a row, column and value
        await mito.getByText('+ Add').first().click();
        await mito.getByText('Column1').click();
        await awaitResponse(page);
        await mito.getByText('+ Add').nth(1).click();
        await mito.getByText('Column2').click();
        await awaitResponse(page);
        await mito.getByText('+ Add').nth(2).click();
        await mito.getByText('Column3').click();
        await awaitResponse(page);

        // Check that the pivot table has been created
        await expect(mito.getByText('Column3 count 2')).toBeVisible();

        // Close the taskpane
        await closeTaskpane(mito);

        // Switch to the OG tab, and then back to the pivot table
        await mito.getByText('test', {exact: true}).click();
        await mito.getByText('test_pivot', { exact: true }).click();

        // Check pivot is being edited
        await checkOpenTaskpane(mito, 'Edit Pivot Table test_pivot');

        // Change count to sum
        await mito.getByText('count', { exact: true }).click();
        await mito.getByText('sum', { exact: true }).click();
        await awaitResponse(page);

        // Check that the pivot table has been updated
        await expect(mito.getByText('Column3 sum 2')).toBeVisible();
    });

    test('Replays Dependent Edits', async ({ page }) => {
        const mito = await getMitoFrameWithTestCSV(page);
        
        await clickButtonAndAwaitResponse(page, mito, { name: 'Pivot' })
        
        await checkOpenTaskpane(mito, 'Create Pivot Table test_pivot');

        // Check new empty tab
        await mito.getByText('test_pivot', { exact: true }).click();
        await expect(mito.getByText('test_pivot', { exact: true })).toBeVisible();
        await expect(mito.getByText('No data in dataframe.')).toBeVisible();
        
        // Add a row, column and value
        await mito.getByText('+ Add').first().click();
        await mito.getByText('Column1').click();
        await awaitResponse(page);
        await mito.getByText('+ Add').nth(1).click();
        await mito.getByText('Column2').click();
        await awaitResponse(page);
        await mito.getByText('+ Add').nth(2).click();
        await mito.getByText('Column3').click();
        await awaitResponse(page);

        // Check that the pivot table has been created
        await expect(mito.getByText('Column3 count 2')).toBeVisible();

        // Add a column
        await mito.locator('[id="mito-toolbar-button-add\\ column\\ to\\ the\\ right"]').getByRole('button', { name: 'Insert' }).click();
        await awaitResponse(page);

        // Check that the pivot table has been updated -- there should be
        // 5 columns from pivot + 1 added
        await expect(mito.locator('.endo-column-header-container')).toHaveCount(6);

        // Switch to the OG tab, and then back to the pivot table
        await mito.getByText('test', {exact: true}).click();
        await mito.getByText('test_pivot', { exact: true }).click();

        // Check pivot is being edited
        await checkOpenTaskpane(mito, 'Edit Pivot Table test_pivot');

        // Change count to sum
        await mito.getByText('count', { exact: true }).click();
        await mito.getByText('sum', { exact: true }).click();
        await awaitResponse(page);

        // Check that the pivot table has been updated
        await expect(mito.getByText('Column3 sum 2')).toBeVisible();

        // Close the pivot taskpane
        await closeTaskpane(mito);

        // Check there are still 6 columns
        await expect(mito.locator('.endo-column-header-container')).toHaveCount(6);
    });
});